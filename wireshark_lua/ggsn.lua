--
-- decoding IP inside ggsn packet
--
-- $Id: 20120722$
-- $Date: 2012-07-22 13:48:12$
-- $Author: Marek Lukaszuk$
--
-- usage:
--    wireshark -X lua_script:ggsn.lua
--
-- any ideas, suggestions for changes, new versions of the protocol
-- please contact Marek Lukaszuk
--
-- version: 20111203

ipggsn_proto = Proto("IPoverGGSN","IP over GGSN")

function ipggsn_proto.dissector(buf,pinfo,tree)
        local offset = 26
        if buf(0,3):uint() == 5064515 and buf(22,2):uint() == 16562 then
          offset = 30
        end
        local inside_dis = Dissector.get ("ip")
        inside_dis:call (buf(offset):tvb(), pinfo, tree)
end

wtap_diss = DissectorTable.get("wtap_encap")
wtap_diss:add(87,ipggsn_proto)

