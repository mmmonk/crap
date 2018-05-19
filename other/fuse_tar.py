#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# http://pythonhosted.org/llfuse/example.html
# https://github.com/python-llfuse/python-llfuse

import errno
import logging
import os
import stat
import tarfile
import time
from argparse import ArgumentParser

try:
  import faulthandler
except ImportError:
  pass
else:
  faulthandler.enable()

# works with version llfuse 1.2
import llfuse

log = logging.getLogger(__name__)

class TarFS(llfuse.Operations):
  """
  """
  def __init__(self, tarname):
    """
    """
    super(TarFS, self).__init__()
    self.tar = None
    if tarname.lower().endswith("gz"):
      self.tar = tarfile.open(tarname, mode="r:gz")
    elif tarname.lower().endswith("bz2"):
      self.tar = tarfile.open(tarname, mode="r:bz2")
    elif tarname.lower().endswith("xz"):
      self.tar = tarfile.open(tarname, mode="r:xz")
    else:
      self.tar = tarfile.open(tarname, mode="r")

    # size used later in statfs syscall for df
    self.whole_size = os.stat(tarname).st_size

    # inodes numbers are indexes from tar.getnames() + 1
    self.delta = llfuse.ROOT_INODE + 1

    # max inode value, if we get something higher we don't need to check anything
    self.max_inode = len(self.tar.getnames()) + self.delta

  def getattr(self, inode, ctx=None):
    """
    """
    entry = llfuse.EntryAttributes()

    # root inode attributes
    if inode == llfuse.ROOT_INODE:
      entry.st_mode = (stat.S_IFDIR | 0o755)
      entry.st_size = 0
      stamp = int(time.time() * 1e9)

    # parameters for inodes inside the tar file
    elif inode < self.max_inode:
      tar_inode = self.tar.getmembers()[inode - self.delta]

      # setting proper mode based on the type of the inode
      entry.st_mode = 0
      if tar_inode.isdir():
        entry.st_mode = stat.S_IFDIR
      elif tar_inode.isreg():
        entry.st_mode = stat.S_IFREG
      elif tar_inode.islnk():
        entry.st_mode = stat.S_IFLNK
      elif tar_inode.issym():
        entry.st_mode = stat.S_IFLNK
      elif tar_inode.isfifo():
        entry.st_mode = stat.S_IFIFO
      elif tar_inode.ischr():
        entry.st_mode = stat.S_IFCHR
      entry.st_mode |= tar_inode.mode

      # inode size
      entry.st_size = tar_inode.size

      # we will use mtime for atime and ctime also
      stamp = (tar_inode.mtime * 1e9)
    else:
      raise llfuse.FUSEError(errno.ENOENT)

    entry.st_atime_ns = stamp
    entry.st_ctime_ns = stamp
    entry.st_mtime_ns = stamp
    entry.st_gid = os.getgid()
    entry.st_uid = os.getuid()
    entry.st_ino = inode

    # because this is read-only FS we can set timeouts to large values
    entry.attr_timeout = 3600
    entry.entry_timeout = 3600

    return entry

  def lookup(self, parent_inode, name, ctx=None):
    """
    """

    # parent_inode needs to be lower then max_inode
    assert parent_inode < self.max_inode

    # special case of '.' inode
    if name == b'.':
      return self.getattr(parent_inode)

    # special case of '..' inode
    idx = parent_inode - self.delta
    if name == b'..':
      # we get the name of the folder above
      p_path = os.path.split(self.tar.getnames()[idx])[0]
      # knowing the name we find the index for it in the list
      idx = self.tar.getnames().index(p_path)
      # index + delta is our inode number
      return self.getattr(idx + self.delta)

    # special case of ROOT inode
    if parent_inode == llfuse.ROOT_INODE:
      prefix = ""

    else:
      prefix = self.tar.getnames()[idx]

    idx = 0
    for fd in self.tar.getnames():
      if os.path.split(fd)[0] == prefix and\
          name == os.path.basename(fd).encode('utf-8'):
        return self.getattr(idx + self.delta)
      idx += 1
    raise llfuse.FUSEError(errno.ENOENT)

  def opendir(self, inode, ctx):
    """
    """

    if inode == llfuse.ROOT_INODE:
      return inode

    elif inode < self.max_inode:
      idx = inode - self.delta
      if self.tar.getmembers()[idx].isdir():
        return inode

    raise llfuse.FUSEError(errno.ENOENT)

  def readdir(self, inode, off):
    """
    """
    if inode == llfuse.ROOT_INODE:
      prefix = ""
    else:
      idx = inode - self.delta
      prefix = self.tar.getnames()[idx]

    idx = 1
    for fd in self.tar.getnames():
      if os.path.split(fd)[0] == prefix:
        if idx > off:
          yield (os.path.basename(fd).encode('utf-8'), self.getattr(idx - 1 + self.delta), idx)
      idx += 1

  def open(self, inode, flags, ctx):
    """
    """
    return inode

  def read(self, fh, off, size):
    """
    """
    idx = fh - self.delta
    fd = self.tar.extractfile(self.tar.getnames()[idx])
    fd.seek(off)
    return fd.read(size)

  def statfs(self, ctx):
    """
    to make output of df nicer
    man 2 statvfs
    """
    stfs = llfuse.StatvfsData()
    stfs.f_bavail = 0
    stfs.f_bfree = 0
    stfs.f_blocks = self.whole_size
    stfs.f_bsize = 4096
    stfs.f_favail = 0
    stfs.f_ffree = 0
    stfs.f_files = self.max_inode
    stfs.f_frsize = 1

    return stfs


def init_logging(debug=False):
  """
  """
  formatter = logging.Formatter('%(asctime)s.%(msecs)03d %(threadName)s: '
                                '[%(name)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  root_logger = logging.getLogger()
  if debug:
    handler.setLevel(logging.DEBUG)
    root_logger.setLevel(logging.DEBUG)
  else:
    handler.setLevel(logging.INFO)
    root_logger.setLevel(logging.INFO)
  root_logger.addHandler(handler)

def parse_args():
  '''Parse command line'''

  parser = ArgumentParser()
  parser.add_argument('tarfile', type=str,
                      help='tarfile to mount')
  parser.add_argument('--mountpoint', type=str,
                      help='Where to mount the file system', default="")
  parser.add_argument('--debug', action='store_true', default=False,
                      help='Enable debugging output')
  parser.add_argument('--debug-fuse', action='store_true', default=False,
                      help='Enable FUSE debugging output')
  return parser.parse_args()


def getmount_point(opt):
  """
  """
  tarfile = os.path.basename(opt.tarfile)
  mpath = opt.mountpoint

  if not mpath:
    (mpath, ext) = os.path.splitext(tarfile)
    if ext and mpath:
      if not os.path.exists(mpath):
        os.mkdir(mpath)
        return mpath
      elif os.path.isdir(mpath):
        return mpath
    raise Exception("Please specify a correct mountpoint")
  return mpath

def main():
  """
  """
  options = parse_args()
  init_logging(options.debug)

  mpath = getmount_point(options)
  tarfs = TarFS(options.tarfile)
  fuse_options = set(llfuse.default_options)
  fuse_options.add('fsname=fuse_tar')
  fuse_options.add('ro')
  if options.debug_fuse:
    fuse_options.add('debug')
  llfuse.init(tarfs, mpath, fuse_options)
  try:
    llfuse.main()
  except:
    llfuse.close(unmount=False)
    raise

  llfuse.close()

if __name__ == '__main__':
  main()
