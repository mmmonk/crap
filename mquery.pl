#!/usr/bin/perl -wW

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

require v5.6.1;

BEGIN { 
        if (eval "use Net::SNMP"){
                die "you don't have Net::SNMP library, you can download it from http://cpan.org\n";
        }
}

use strict;

my $OIDsys             = '1.3.6.1.2.1.1.1.0';
my $OIDmac             = '1.3.6.1.2.1.2.2.1.6.2';
my $OIDmodel           = '1.3.6.1.2.1.1.5.0';
my $OIDcpemac          = '1.3.6.1.2.1.17.4.3.1.1';
my $OIDtime            = '1.3.6.1.2.1.69.1.1.2.0';
my $OIDreset           = '1.3.6.1.2.1.69.1.1.3.0';
my $OIDsn              = '1.3.6.1.2.1.69.1.1.4.0';
my $OIDSTPControl      = '1.3.6.1.2.1.69.1.1.5.0';
my $OIDfile            = '1.3.6.1.2.1.69.1.3.2.0';
my $OIDSwAdminStatus   = '1.3.6.1.2.1.69.1.3.3.0';
my $OIDSwOperStatus    = '1.3.6.1.2.1.69.1.3.4.0';
my $OIDsoftver         = '1.3.6.1.2.1.69.1.3.5.0';
my $OIDServerBootState = '1.3.6.1.2.1.69.1.4.1.0';
my $OIDSrvDHCP         = '1.3.6.1.2.1.69.1.4.2.0';
my $OIDSrvTime         = '1.3.6.1.2.1.69.1.4.3.0';
my $OIDSrvTFTP         = '1.3.6.1.2.1.69.1.4.4.0';
my $OIDcfgfile         = '1.3.6.1.2.1.69.1.4.5.0';
my $OIDFilterIpDefault = '1.3.6.1.2.1.69.1.6.3.0';
my $OIDIpForwarding    = '1.3.6.1.2.1.4.1.0';

my $OIDmifstat     = '1.3.6.1.2.1.2.2.1';
my $OIDifstat      = "$OIDmifstat.1";
my $OIDmlogs       = '1.3.6.1.2.1.69.1.5.8.1';
my $OIDlogs        = "$OIDmlogs.2";
my $OIDmIPfilters  = '1.3.6.1.2.1.69.1.6.4.1';
my $OIDIPfilter    = "$OIDmIPfilters.2";
my $OIDmQOS        = '1.3.6.1.2.1.10.127.1.1.3.1';
my $OIDQOS         = "$OIDmQOS.2";
my $OIDmService    = '1.3.6.1.2.1.10.127.1.2.3.1';
my $OIDService     = "$OIDmService.2";
my $OIDmDownStream = '1.3.6.1.2.1.10.127.1.1.1.1';
my $OIDDownStream  = "$OIDmDownStream.1";
my $OIDmUpStream   = '1.3.6.1.2.1.10.127.1.1.2.1';
my $OIDUpStream    = "$OIDmUpStream.1";
my $OIDmSigQ       = '1.3.6.1.2.1.10.127.1.1.4.1';
my $OIDSigQ        = "$OIDmSigQ.1";
my $OIDmCMstatus   = '1.3.6.1.2.1.10.127.1.2.2.1';
my $OIDCMstatus    = "$OIDmCMstatus.1";
my $OIDmSFpktClass = '1.3.6.1.2.1.10.127.7.1.1.1';
my $OIDSFpktClass  = "$OIDmSFpktClass.2";

my %ifstatus = (
    1 => "Up",
    2 => "Down",
    3 => "Other",
    4 => "Unknown",
    5 => "Dormant"
);

my %SwAdminStatus = (
    1 => "upgradeFromMgt",
    2 => "allowProvisioningUpgrade",
    3 => "ignoreProvisioningUpgrade"
);

my %SwOperStatus = (
    1 => "inProgress",
    2 => "completeFromProvisioning",
    3 => "completeFromMgt",
    4 => "failed",
    5 => "other"
);

my %ServerBootState = (
    1  => "operational",
    2  => "disabled",
    3  => "waitingForDhcpOffer",
    4  => "waitingForDhcpResponse",
    5  => "waitingForTimeServer",
    6  => "waitingForTftp",
    7  => "refusedByCmts",
    8  => "forwardingDenied",
    9  => "other",
    10 => "unknown"
);

my %evlevel = (
    1 => "emergency  ",
    2 => "alert      ",
    3 => "critical   ",
    4 => "error      ",
    5 => "warning    ",
    6 => "notice     ",
    7 => "information",
    8 => "debug      "
);

my %FilterIpControl = (
    1 => "drop ",
    2 => "allow",
    3 => "poli "
);

my %FilterIpDirection = (
    1 => "in  ",
    2 => "out ",
    3 => "both"
);

my %TruthValue = (
    1 => "true ",
    2 => "false"
);

my %RowStatus = (
    1 => "active",
    2 => "notInSrv",
    3 => "notReady",
    4 => "create&Go",
    5 => "create&W8",
    6 => "destroy"
);

my %STPControl = (
    1 => "stEnabled",
    2 => "noStFilterBpdu",
    3 => "noStPassBpdu"
);

my %DownChannelModulation = (
    1 => "unknown",
    2 => "other",
    3 => "qam64",
    4 => "qam256"
);

my %DownChannelInterleave = (
    1 => "unknown",
    2 => "other",
    3 => "taps8Inc16",
    4 => "taps16Inc8",
    5 => "taps32Inc4",
    6 => "taps64Inc2",
    7 => "taps128Inc1",
    8 => "taps12Inc17"
);

my %CmStatusValue = (
    1  => "other",
    2  => "notReady",
    3  => "notSynchronized",
    4  => "phySynchronized",
    5  => "usParamAcquired",
    6  => "rangingComplete",
    7  => "ipComplete",
    8  => "todEstablished",
    9  => "secEstablished",
    10 => "paramTransComp",
    11 => "regComplete",
    12 => "operational",
    13 => "accessDenied"
);

my %FilterIpDefault = (
    1 => "drop",
    2 => "allow"
);

my %IfName = (
    6   => "Eth",
    24  => "Lo",
    127 => "CMac",
    128 => "CDown",
    129 => "CUp",
    160 => "USB"
);

my $query = shift;
exit if ( !$query );

my $readcom = shift;
$readcom = "public" unless ($readcom);

my ( $session, $error ) = Net::SNMP->session(
    -timeout   => 3,
    -retries   => 5,
    -hostname  => $query,
    -community => $readcom,
    -port      => 161,
    -version   => 2,
    -translate => 0
);

if ( !defined($session) ) {
    $session->close;
    exit;
}

my $re = $session->get_request(
    -varbindlist => [
        $OIDmodel,      $OIDsoftver, $OIDsys,
        $OIDmac,        $OIDsn,      $OIDServerBootState,
        $OIDSTPControl, $OIDtime,    $OIDcfgfile
    ]
);
exit if ( !$re );

my $cmmac = $re->{$OIDmac};

if ( $cmmac =~ /^0x.+/ ) {
    $cmmac =~ s/0x//;
}
else {
    $cmmac = convmac($cmmac);
}

print "IP	  : " . $query . "
MAC  	  : " . $cmmac . "
SN	  : " . $re->{$OIDsn} . "
Sys	  : " . $re->{$OIDsys} . "
Model	  : " . $re->{$OIDmodel} . "
Time      : " . ( decodetime( $re->{$OIDtime} ) ) . " 
SoftVer	  : " . $re->{$OIDsoftver} . "
State	  : " . $ServerBootState{ $re->{$OIDServerBootState} } . "
STPctl    : " . $STPControl{ $re->{$OIDSTPControl} } . "
CfgFile   : " . $re->{$OIDcfgfile} . "\n";

$re = $session->get_request(
    -varbindlist => [
        $OIDSwAdminStatus, $OIDSwOperStatus, $OIDSrvDHCP,
        $OIDSrvTime,       $OIDSrvTFTP,      $OIDIpForwarding
    ]
);

print "SwAdmin   : " . $SwAdminStatus{ $re->{$OIDSwAdminStatus} } . "
SwOper    : " . $SwOperStatus{ $re->{$OIDSwOperStatus} } . "
DHCP Srv  : " . $re->{$OIDSrvDHCP} . "
Time Srv  : " . $re->{$OIDSrvTime} . "
TFTP Srv  : " . $re->{$OIDSrvTFTP} . "
Forwarding: " . $TruthValue{ $re->{$OIDIpForwarding} } . "\n";

#### CPE MAC
$re = $session->get_table( -baseoid => $OIDcpemac );
if ($re) {
    print "\nCPE MAC:\n------------\n";
    foreach ( keys %$re ) {
        next unless ($_);
        my $cmac = $re->{$_};
        if ( $cmac =~ /^0x/ ) {
            $cmac =~ s/^0x//;
        }
        else {
            $cmac = convmac($cmac);
        }
        print "$cmac\n";
    }
}

#### Interface statistics
$re = $session->get_table( -baseoid => $OIDifstat );
if ($re) {
    print "\nInterface Status:\n";
    print
"                                                                 |                         IN                                |                        OUT\n";
    print
"I|Type |MTU |Speed  |PhysAdd     |AdminS |OperS  |LastChange     |Oct      |Ucast    |NUcast   |Disc     |Err      |Unkn     |Oct      |Ucast    |NUcast   |Disc     |Err      |QLen\n";
    print
"------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
        my $re2 = rowget( $OIDmifstat, $loid, 3, 21 );

        my $row = "" . $re->{$_};
        for ( my $counter = 3 ; $counter <= 21 ; $counter++ ) {
            my $value = $re2->{"$OIDmifstat.$counter.$loid"} || "0";

            if ( $counter == 3 ) {
                if ( exists( $IfName{$value} ) ) {
                    $value = $IfName{$value};
                }
                $value = $value . " " x ( 5 - length($value) );
            }

            if ( $counter == 5 ) {
                $value = hspeed($value);
                $value = $value . " " x ( 7 - length($value) );
            }

            if ( $counter == 6 ) {
                if ( $value ne "0" ) {
                    if ( $value =~ /^0x.+/ ) {
                        $value =~ s/0x//;
                    }
                    else {
                        $value = convmac($value);
                    }
                }
                $value = $value . " " x ( 12 - length($value) );
            }

            if ( $counter == 7 or $counter == 8 ) {
                $value = $ifstatus{$value};
                $value = $value . " " x ( 7 - length($value) );
            }

            if ( $counter == 9 ) {
                $value = htime($value);
            }

            if ( $counter == 10 or $counter == 16 ) {
                if ( $value > 1073741824 ) {
                    $value =
                      ( int( ( ( $value / 1073741824 ) * 100 ) / 1 ) / 100 )
                      . " G";
                }
                else {
                    if ( $value > 1048576 ) {
                        $value =
                          ( int( ( ( $value / 1048576 ) * 100 ) / 1 ) / 100 )
                          . " M";
                    }
                    else {
                        if ( $value > 1024 ) {
                            $value =
                              ( int( ( ( $value / 1024 ) * 100 ) / 1 ) / 100 )
                              . " k";
                        }
                    }
                }
            }

            if ( $counter >= 10 and $counter < 21 ) {
                $value = $value . " " x ( 9 - length($value) );
            }

            $row .= "|$value";
        }
        print "$row\n";
    }
}

#### CM Status
$re = $session->get_table( -baseoid => $OIDCMstatus );
if ($re) {
    print "\nCM Status:\n";
    print
"StatusValue    |Code    |TxPower   |Resets  |LostSync|InvMaps |InvUcds |InvRngResp|InvRegResp|T1      |T2      |T3      |T4      |RngAborteds\n";
    print
"---------------------------------------------------------------------------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
        my $re2 = rowget( $OIDmCMstatus, $loid, 2, 14 );

        my $row = ""
          . $CmStatusValue{ $re->{$_} }
          . " " x ( 15 - length( $CmStatusValue{ $re->{$_} } ) );
        for ( my $counter = 2 ; $counter <= 14 ; $counter++ ) {
            my $value = $re2->{"$OIDmCMstatus.$counter.$loid"} || "0";
            if ( $counter == 3 ) {
                my $uppwr = $value / 10;
                if (   ( $uppwr < 45 and $uppwr >= 30 )
                    or ( $uppwr <= 58 and $uppwr > 55 ) )
                {
                    $value = "$value\!  dBmV";
                }
                else {
                    if ( $uppwr > 58 or $uppwr < 30 ) {
                        $value = "$value\!\! dBmV";
                    }
                    else {
                        $value = "$value   dBmV";
                    }
                }
            }
            $value = unpack( "C*", $value ) if ( $counter == 2 );
            $row .= "|$value";

            if ( $counter == 8 or $counter == 9 or $counter == 14 ) {
                $row .= " " x ( 10 - length($value) );
                next;
            }
            $row .= " " x ( 8 - length($value) );
        }
        print "$row\n";

    }
}

#### Signal Quality
$re = $session->get_table( -baseoid => $OIDSigQ );
if ($re) {
    print "\nSignal Quality:\n";
    print
"Contention     |Unerroreds     |Correcteds     |Uncorrectables |SignalNoise    |MicReflections |EqualizationData\n";
    print
"-----------------------------------------------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
        my $re2 = rowget( $OIDmSigQ, $loid, 2, 7 );

        my $row = ""
          . ( $TruthValue{ $re->{$_} } )
          . " " x ( 15 - length( $TruthValue{ $re->{$_} } ) );
        for ( my $counter = 2 ; $counter <= 7 ; $counter++ ) {
            my $value = $re2->{"$OIDmSigQ.$counter.$loid"} || "0";
            if ( $counter == 5 ) {
                $value = $value / 10;
                if ( ( $value >= 28 and $value < 30 ) or ( $value > 41 ) ) {
                    $value = "$value\!";
                }
                else {
                    if ( $value < 28 ) {
                        $value = "$value\!\!";
                    }
                }
            }
            if ( $counter == 6 ) {
                if ( $value <= 90 and $value > 40 ) {
                    $value = "$value\!";
                }
                else {
                    if ( $value > 90 ) {
                        $value = "$value\!\!";
                    }
                }
            }
            $value = unpack( "h", $value ) if ( $counter == 7 );
            $row .= "|$value" . " " x ( 15 - length($value) );
        }
        print "$row\n";
    }
}

#### Dowstream
$re = $session->get_table( -baseoid => $OIDDownStream );
if ($re) {
    print "\nDownstream:\n";
    print
"Id             |Frequency      |Width          |Modulation     |Interleave     |Power          \n";
    print
"-----------------------------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
        my $re2 = rowget( $OIDmDownStream, $loid, 2, 6 );

        my $row = "" . $re->{$_} . " " x ( 15 - length( $re->{$_} ) );
        for ( my $counter = 2 ; $counter <= 6 ; $counter++ ) {
            my $value = $re2->{"$OIDmDownStream.$counter.$loid"} || "0";
            $value = ( $value / 1000000 ) . " Mhz"  if ( $counter == 2 );
            $value = ( $value / 1000000 ) . " Mhz"  if ( $counter == 3 );
            $value = $DownChannelModulation{$value} if ( $counter == 4 );
            $value = $DownChannelInterleave{$value} if ( $counter == 5 );
            if ( $counter == 6 ) {
                my $dwpwr = $value / 10;
                if (   ( $dwpwr < -10 and $dwpwr >= -19 )
                    or ( $dwpwr <= 19 and $dwpwr > 15 ) )
                {
                    $value = "$value\!";
                }
                else {
                    if ( $dwpwr > 19 or $dwpwr < -19 ) {
                        $value = "$value\!\!";
                    }
                }
                $value = $value . " dBmV";
            }
            $row .= "|$value" . " " x ( 15 - length($value) );
        }
        print "$row\n";
    }
}

#### Upstream
$re = $session->get_table( -baseoid => $OIDUpStream );
if ($re) {
    print "\nUpstream:\n";
    print
"Id  |Frequency   |Width     |ModProf |SlotSize|TxTimOff|RngBaOfS|RngBaOfE|TxBaOffS|TxBaOffE\n";
    print
"-------------------------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
        my $re2 = rowget( $OIDmUpStream, $loid, 2, 10 );

        my $row = "" . $re->{$_} . " " x ( 4 - length( $re->{$_} ) );
        for ( my $counter = 2 ; $counter <= 10 ; $counter++ ) {
            my $value = $re2->{"$OIDmUpStream.$counter.$loid"} || "0";
            $value = ( $value / 1000000 ) . " Mhz" if ( $counter == 2 );
            $value = ( $value / 1000000 ) . " Mhz" if ( $counter == 3 );
            $row .= "|$value";
            if ( $counter == 2 ) {
                $row .= " " x ( 12 - length($value) );
                next;
            }
            if ( $counter == 3 ) {
                $row .= " " x ( 10 - length($value) );
                next;
            }
            $row .= " " x ( 8 - length($value) );
        }
        print "$row\n";
    }
}

#### Service
$re = $session->get_table( -baseoid => $OIDService );
if ($re) {
    print "\nService:\n";
    print
"QosProfile     |TxSlotsImmed   |TxSlotsDed     |TxRetries      |TxExceededs    |RqRetries      |RqExceededs\n";
    print
"-----------------------------------------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+\.\d+)$/$1/;
        my $re2 = rowget( $OIDmService, $loid, 3, 8 );

        print "" . $re->{$_} . " " x ( 15 - length( $re->{$_} ) );
        for ( my $counter = 3 ; $counter <= 8 ; $counter++ ) {
            my $value = $re2->{"$OIDmService.$counter.$loid"} || "0";
            print "|$value";
            print " " x ( 15 - length($value) );
        }
        print "\n";
    }
}

#### QOS DOCSIS 1.0
$re = $session->get_table( -baseoid => $OIDQOS );
if ($re) {
    print "\nQOS:\n";
    print
"Priority  |MaxUpBW   |GuarUpBW  |MaxDownBW |GuarDownBW|BP        |Status\n";
    print
"------------------------------------------------------------------------\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;

        my $re2 = rowget( $OIDmQOS, $loid, 3, 5 );

        my $row = "" . $re->{$_} . " " x ( 10 - length( $re->{$_} ) );
        for ( my $counter = 3 ; $counter <= 5 ; $counter++ ) {
            my $value = $re2->{"$OIDmQOS.$counter.$loid"} || "0";
            $row .= "|$value" . " " x ( 10 - length($value) );
        }

        $row .= "|0" . " " x 9;

        $re2 = rowget( $OIDmQOS, $loid, 7, 8 );

        for ( my $counter = 7 ; $counter <= 8 ; $counter++ ) {
            my $value = $re2->{"$OIDmQOS.$counter.$loid"} || "0";
            $value = $TruthValue{$value} if ( $counter == 7 );
            $value = $RowStatus{$value}  if ( $counter == 8 );
            $row .= "|$value" . " " x ( 10 - length($value) );
        }

        print "$row\n";
    }
}

#### Service Flow Class
$re = $session->get_table( -baseoid => $OIDSFpktClass );
if ($re) {
    print "\nService Flow Classes:\n";
    print
"Dir|Pri|TosL|TosH|TosM|Prot|Source Address |Source Net Mask|Dest Address   |Dest Net Mask  |SPrtL|SPrtH|DPrtL|DPrtH|DestMacAddr |DestMacMask |SrcMacAddr  |EtTy|\n";
    foreach ( sort keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+\.\d+\.\d+)$/$1/;
        my $re2 = rowget( $OIDmSFpktClass, $loid, 3, 20 );

        my $row = "" . $re->{$_} . " " x ( 3 - length( $re->{$_} ) );
        for ( my $counter = 3 ; $counter <= 20 ; $counter++ ) {
            my $value = $re2->{"$OIDmSFpktClass.$counter.$loid"};
            $value = unpack( "C",  $value ) if ( $counter == 3 );
            $value = unpack( "h",  $value ) if ( $counter == 4 );
            $value = unpack( "h",  $value ) if ( $counter == 5 );
            $value = unpack( "h",  $value ) if ( $counter == 6 );
            $value = unpack( "H*", $value ) if ( $counter == 16 );
            $value = unpack( "H*", $value ) if ( $counter == 17 );
            $value = unpack( "H*", $value ) if ( $counter == 18 );
            if ( $counter =~ /(^8|^9|^10|^11)$/ ) {
                $row .= "|$value" . " " x ( 15 - length($value) );
                next;
            }
            if ( $counter =~ /(^12|^13|^14|^15)$/ ) {
                $row .= "|$value" . " " x ( 5 - length($value) );
                next;
            }
            if ( $counter =~ /(^4|^5|^6|^7)$/ ) {
                $row .= "|$value" . " " x ( 4 - length($value) );
                next;
            }
            $row .= "|$value" . " " x ( 3 - length($value) );
        }

        $re2 = rowget( $OIDmSFpktClass, $loid, 22, 27 );
        for ( my $counter = 22 ; $counter <= 27 ; $counter++ ) {
            my $value = $re2->{"$OIDmSFpktClass.$counter.$loid"};
            $row .= "|$value";
        }

        print "$row\n";
    }
}

$re = $session->get_request( -varbindlist => [$OIDFilterIpDefault] );
if ($re) {
    print "\n\nDefault IP Filter Policy is: "
      . ( $FilterIpDefault{ $re->{$OIDFilterIpDefault} } ) . "\n";
}

#### IP Filter
$re = $session->get_table( -baseoid => $OIDIPfilter );
if ($re) {
    print "\nIP Filters:\n";
    print
"Idx|Act  |If |Dir |Broad|Source Address |Source Net Mask|Dest Address   |Dest Net Mask  |Protocol|SPrtL|SPrtH|DPrtL|DPrtH|Match  |Tos|TosM|Cont |PolID\n";
    print
"------------------------------------------------------------------------------------------------------------------------------------------------------\n";
    foreach ( sort snmplastoid keys %$re ) {
        next unless ($_);
        ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
        my $re2 = rowget( $OIDmIPfilters, $loid, 3, 20 );

        my $row = "" . $re->{$_} . " " x ( 3 - length( $re->{$_} ) );
        for ( my $counter = 3 ; $counter <= 20 ; $counter++ ) {
            my $value = $re2->{"$OIDmIPfilters.$counter.$loid"};
            $value = $FilterIpControl{$value}   if ( $counter == 3 );
            $value = $FilterIpDirection{$value} if ( $counter == 5 );
            $value = $TruthValue{$value}        if ( $counter == 6 );
            $value = unpack( "H", $value ) if ( $counter == 17 );
            $value = unpack( "H", $value ) if ( $counter == 18 );
            $value = $TruthValue{$value} if ( $counter == 19 );
            if ( $counter == 11 ) {

                if ( $value == 256 ) {
                    $value = "any";
                }
                else {
                    $value = getprotobynumber($value);
                }
            }
            if ( $counter == 4 ) {
                $value = "any" if ( $value == 0 );
            }

            $row .= "|$value";

            if ( $counter == 11 ) {
                $row .= " " x ( 8 - length($value) );
                next;
            }

            if (   $counter == 7
                or $counter == 8
                or $counter == 9
                or $counter == 10 )
            {
                $row .= " " x ( 15 - length($value) );
                next;
            }

            if (   $counter == 6
                or $counter == 12
                or $counter == 13
                or $counter == 14
                or $counter == 15 )
            {
                $row .= " " x ( 5 - length($value) );
                next;
            }
            if ( $counter == 16 ) {
                $row .= " " x ( 7 - length($value) );
                next;
            }
            if ( $counter == 5 or $counter == 18 ) {
                $row .= " " x ( 4 - length($value) );
                next;
            }

            $row .= " " x ( 3 - length($value) );
        }
        print "$row\n";
    }
}

#### LOGS
$re = $session->get_table( -baseoid => $OIDlogs );
exit unless ($re);
print "\nLogs:\n";
print
  "First Time         |Last Time          |Count   |Level      |Description\n";
print
  "------------------------------------------------------------------------\n";
foreach ( sort snmplastoid keys %$re ) {
    next unless ($_);
    ( my $loid = $_ ) =~ s/.+?\.(\d+)$/$1/;
    my $re2 = rowget( $OIDmlogs, $loid, 3, 7 );

    my $first = decodetime( $re->{$_} );
    my $last  = decodetime( $re2->{"$OIDmlogs.3.$loid"} );
    print "$first|$last|"
      . $re2->{"$OIDmlogs.4.$loid"} . "\t|"
      . $evlevel{ $re2->{"$OIDmlogs.5.$loid"} } . "|"
      . $re2->{"$OIDmlogs.7.$loid"} . "\n";
}

$session->close;

sub decodetime {
    my $data = shift;
    $data = unpack( "H*", $data );

    $data =~ s/(....)(..)(..)(..)(..)(..).*/$1:$2:$3:$4:$5:$6/;

    my ($sec,$min,$hour,$mday,$mon,$year);

    ( $year, $mon, $mday, $hour, $min, $sec ) = map( hex, split( ":", $data ) );

    $hour = "0$hour" if $hour < 10;
    $mday = "0$mday" if $mday < 10;
    $mon  = "0$mon"  if $mon < 10;
    $min  = "0$min"  if $min < 10;
    $sec  = "0$sec"  if $sec < 10;

    return "$year/$mon/$mday $hour:$min:$sec";
}

sub convmac {
    my $badmac = shift;
    my @tmp;
    my $i = 0;
    foreach ( split( '', $badmac ) ) {
        my $c = sprintf( "%2x", ord($_) );
        $c =~ s/ /0/;
        $tmp[ $i++ ] = $c;
    }
    my $newmac = join( '', @tmp );
    return $newmac;
}

sub rowget {
    my $OIDmain = shift;
    my $OIDend  = shift;
    my $cstart  = shift;
    my $cend    = shift;

    my $tmpre;
    my $tquery = '$tmpre=$session->get_request(-varbindlist=>[';
    for ( my $counter = $cstart ; $counter <= $cend ; $counter++ ) {
        $tquery .= "'$OIDmain.$counter.$OIDend'";
        $tquery .= "," if ( $counter < $cend );
    }
    $tquery .= "]);";

    eval $tquery;
    print $@ if ($@);

    return $tmpre;
}

sub snmplastoid {
    ( my $a1 = $a ) =~ s/.*?\.(\d+)$/$1/;
    ( my $b1 = $b ) =~ s/.*?\.(\d+)$/$1/;

    $a1 <=> $b1;
}

sub hspeed {
    my $speed = shift;

    if ( $speed > 1024 ) {
        $speed = $speed / 1024;
        if ( $speed > 1024 ) {
            $speed = $speed / 1024;
            $speed = sprintf( "%.2f M", $speed );
        }
        else {
            $speed = sprintf( "%.2f K", $speed );
        }
    }

    return $speed;
}

sub htime {
    my $vartime = shift;
    my ($sec,$min,$hour,$mday,$mon,$year);

    ( $sec, $min, $hour, $mday, $mon, $year, undef, undef, undef ) =
      localtime($vartime);
    $year += 1900;
    $mon  += 1;
    $hour = "0$hour" if $hour < 10;
    $mday = "0$mday" if $mday < 10;
    $mon  = "0$mon"  if $mon < 10;
    $min  = "0$min"  if $min < 10;
    $sec  = "0$sec"  if $sec < 10;
    my $ret = $year . $mon . $mday . " " . $hour . $min . $sec;
    return $ret;
}

