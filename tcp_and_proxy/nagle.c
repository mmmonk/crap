/*

  $Id$

*/

#include <fcntl.h>
#include <netdb.h>
#include <netinet/tcp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

#define BUFFSIZE 4096 

void die (char *mesg){
  perror(mesg);
  exit(1);
}

int main (int argc, char **argv) {

  int sock,retval,len;
  struct addrinfo hints;
  struct addrinfo *rp;
  struct timeval tv;
  fd_set rfds, wfds; 
  char* buff[BUFFSIZE];
  int state = 1;

  if (argc != 3) {
    fprintf(stderr, "usage: %s <server_ip> <port>\n",argv[0]);
    exit(1);
  }

  memset(&hints,0,sizeof(hints));
  hints.ai_family = AF_UNSPEC;    /* Allow IPv4 or IPv6 */
  hints.ai_socktype = SOCK_STREAM; 
  hints.ai_flags = 0;
  hints.ai_protocol = 0; 

  if (getaddrinfo(argv[1],argv[2],&hints,&rp) != 0)
    die("getaddrinfo()");
 
  if ((sock = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol)) < 0) 
    die("socket()");
  
  if (setsockopt(sock,IPPROTO_TCP, TCP_CORK,&state,sizeof(state)) <0)
    die("setsockopt()");
 
  if (connect(sock,rp->ai_addr,rp->ai_addrlen) == -1)
    die("connect()");

  
//  flags = fcntl(sock, F_GETFL, 0);
  fcntl(sock, F_SETFL, O_NONBLOCK);
  fcntl(0, F_SETFL, O_NONBLOCK);
  fcntl(1, F_SETFL, O_NONBLOCK);

  for(;;){

    tv.tv_sec = 30;
    tv.tv_usec = 0;

    FD_ZERO(&rfds);
    FD_ZERO(&wfds);
    FD_SET(0, &rfds);
    FD_SET(sock, &rfds);
//    FD_SET(1, &wfds);
    FD_SET(sock, &wfds);
    
    retval = select(sock+1, &rfds, &wfds, NULL, &tv);

    if (retval == -1) {

      perror("select()");

    } else if (retval) {

      if (FD_ISSET(0,&rfds) && FD_ISSET(sock,&wfds)) {

        len = read(0,buff,sizeof(buff));

        if (len < 1){
          shutdown(sock,SHUT_RDWR);
          exit(0);
        }

        send(sock,buff,len,0); 

      } 
      
      if (FD_ISSET(sock,&rfds)) {

        len = recv(sock,buff,sizeof(buff),0);

        if (len <= 0){
          shutdown(sock,SHUT_RDWR);
          exit(0);
        }

        write(1,buff,len); 

      }
    }
  }
  
  exit(0);
}
