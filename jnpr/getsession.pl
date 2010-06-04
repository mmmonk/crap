#!/usr/bin/perl 

use strict;
use warnings;

my $file=shift;

my $sess=0;

###   all the data for this script can be found in the file ./include/session.h 

my @natflag1=(
	'time_no_refresh',
	'use_hw_3way_refresh',
	'sess_no_log',
	'to_be_invalid',
	'loop_dip_mip',
	'send_reset',
	'transparent',
	'half_open',

	'tcp_3way_refresh',
	'port_no_xlate',
	'loop',
	'media_signal',
	'incoming_dip',
	'use_hw_ageout',
	'route',
	'syn_sent',

	'synced',
	'no_ftp_put',
	'use_hw_sess',
	'media_channel',
	'gen_gate',
	'fin_sent',
	'backup_pport',
	'ftp_pasv',

	'backup',
	'no_ftp_get',
	'trp_tentative',
	'tunnel',
	'from_gate',
	'auth',
	'invalid',
	'urlblock_on'
);

my @natflag2 = (
	'idp_flag',
	'data_channel',
	'pak_no_forw',
	'media_control_chanel',

	'mac_has_vlan',
	'control_channel',
	'in_content_strip_mode',
	'free_from_mng',

	'nsrp_forw_sess',
	'xlate_rsm_flag',
	'p2mp_sess',
	'no_hw_sess',

	'time_sync_state',
	'asp_flag',
	'ftp_extended',
	'sess_was_authed'
);

my @natflag3 = (
	' ',
	'url_continuation',
	'sess_ageout_phase2',
	'h323_ras_mark',

	' ',
	'sess_was_jps_authed',
	'static_sess',
	'mac_flood',

	' ',
	'dns_xlate_aaaa2a',
	'mng_session',
	'installed_into_ager',

	'idp_sess',
	'dns_xlate_ptr6',
	'thru_ipsec_sess',
	'in_use'
);

my @nspflag = (
	'loopback',
	'free',
	'shape_on',
	'mac_cache',
	'ipsec_alg',
	'l2info_is_arp',
	' ',
	' ',

	'vlan_tag',
	'invalid_if',
	'frag_merge_needed',
	'force_route',
	'rsm_tcp_buf_hold',
	'ras_incoming_dip',
	' ',
	' ',

	'flag_ipv6',
	'flow_deny_except_fin_ack',
	'need_reassemble',
	'l2_ready',
	'rsm_tcp_slow_proxy',
	'police_on',
	' ',
	' ',

	'initiate_side',
	'from_self',
	'flow_deny',
	'syn_open',
	'mcast_encap',
	'gwv6',
	'l2info_is_nd6',
	'src_xlate'
);


while(<>){
	print;
	chomp;
#       id 173184/s0*,vsys 0,flag 10200440/0000/0003,policy 39,time 5556, dip 0 module 0
	if (/^id \d+.+?vsys.+?flag.+?policy.+?time.+?dip/){
		s/^id (\d+\/.+?),\s*vsys (\d+),\s*flag (.+?),\s*policy (\d+),\s*time (\d+),\s*dip (.+?)/$1;$2;$3;$4;$5;$6/;
		# index
		# 0 - session id
		# 1 - vsys
		# 2 - flag
		# 3 - policy id
		# 4 - time
		# 5 - dip + rest
		
		my @a=split(';',$_);
		
		($sess=$a[0])=~s/(\d+)\/.*/$1/;
		
		$a[0]=~s/\d+\/(.+)/$1/;
		print "---------------------------------\n";
    print $sess,": ".$a[0].", vsys ".$a[1].", flag ".$a[2].", policy ".$a[3].", time ".($a[4]*2)." sec, dip ".$a[5]."\n";
		print $sess,": natflag ".$a[2]." = ";		

		# http://kb.juniper.net/KB8349

		my @natflag=split '/',$a[2];

		# nat flag 1

		my @nfchars=split '',$natflag[0]; 
		for (my $i=0;$i<8;$i++){
			if ($nfchars[$i] =~ /^[fca98]$/i ){
				print $natflag1[$i]," ";
			}
			if ($nfchars[$i] =~ /^[fc654]$/i ) {
				print $natflag1[$i+8]," ";
			}
			if ($nfchars[$i] =~ /^[fa632]$/i ) {
				print $natflag1[$i+16]," ";
			}
			if ($nfchars[$i] =~ /^[f9531]$/i ) {
				print $natflag1[$i+24]," ";
			}
		}	
		print "/ ";

		# nat flag 2
		
		@nfchars=split '',$natflag[1]; 
		for (my $i=0;$i<4;$i++){
			if ($nfchars[$i] =~ /^[fca98]$/i ){
				print $natflag2[$i]," ";
			}
			if ($nfchars[$i] =~ /^[fc654]$/i ) {
				print $natflag2[$i+4]," ";
			}
			if ($nfchars[$i] =~ /^[fa632]$/i ) {
				print $natflag2[$i+8]," ";
			}
			if ($nfchars[$i] =~ /^[f9531]$/i ) {
				print $natflag2[$i+12]," ";
			}
		}	
		print "/ ";

		# nat flag 3

		@nfchars=split '',$natflag[2]; 
		for (my $i=0;$i<4;$i++){
			if ($nfchars[$i] =~ /^[fca98]$/i ){
				print $natflag3[$i]," ";
			}
			if ($nfchars[$i] =~ /^[fc654]$/i ) {
				print $natflag3[$i+4]," ";
			}
			if ($nfchars[$i] =~ /^[fa632]$/i ) {
				print $natflag3[$i+8]," ";
			}
			if ($nfchars[$i] =~ /^[f9531]$/i ) {
				print $natflag3[$i+12]," ";
			}
		}	
		print "\n";
	}
	
	if (/^ if \d+\(nspflag /){
		s/^ if (\d+)\(nspflag (.+?)\):(.+?),(\d+),(.+?),sess token (\d+),vlan (\d+),tun (\d+),vsd (\d+),route (\d+)/$1;$2;$3;$4;$5;$6;$7;$8;$9;$10/;
	
		# index:
		# 0 - interface id
		# 1 - nspflag 
		# 2 - IP addresses and ports
		# 3 - protocol number
		# 4 - mac address
		# 5 - session token
		# 6 - vlan id
		# 7 - tunnel id
		# 8 - vsd id
		# 9 - route id
		# 10 - wsf 
	
		my @a=split ';',$_;
	
		print $sess,": $_\n"; 
		print $sess,": nspflag ".$a[1]." = ";

		my @nspfchars=split '',$a[1];

		my $i=length($a[1])-1;
		foreach my $nspchar (@nspfchars){
			if ($nspchar =~ /^[fca98]$/i ){
				print $nspflag[$i]," ";
			}
			if ($nspchar =~ /^[fc654]$/i ) {
				print $nspflag[$i+8]," ";
			}
			if ($nspchar =~ /^[fa632]$/i ) {
				print $nspflag[$i+16]," ";
			}
			if ($nspchar =~ /^[f9531]$/i ) {
				print $nspflag[$i+24]," ";
			}
			$i--;	
		}
		print "\n";
	}
}
