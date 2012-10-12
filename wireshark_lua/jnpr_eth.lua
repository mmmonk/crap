--
-- decoding correctly juniper ethernet packets
--
-- $Id: 20121012$
-- $Date: 2012-10-12 12:22:35$
-- $Author: Marek Lukaszuk$
--

jnpreth83_proto = Proto("JnprEth83","Junpiper Ethernet83")

function jnpreth83_proto.dissector(buf,pinfo,tree)

        local inside_dis = Dissector.get("eth")
        local offset = 22
        if buf(3,1):uint() == 131 then
          inside_dis = Dissector.get("ip")
          offset = 26
        end
        inside_dis:call (buf(offset):tvb(), pinfo, tree)
end

wtap_diss = DissectorTable.get("wtap_encap")
wtap_diss:add(83,jnpreth83_proto)

