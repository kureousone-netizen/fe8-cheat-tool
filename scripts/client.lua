local server = socket.bind('127.0.0.1', 8888)
server:listen() 
server:add('received', function()
    local client = server:accept()
    client:add('received', function()
        local data = client:receive(1024)
        if data then
            for line in data:gmatch('[^\n]+') do
                local prefix, address, value = line:match('(%w%w)(%w+) (%w+)')
                if address and value then
                    local real_address = '02' .. address
                    if prefix == '82' then
                        emu:write16(tonumber(real_address, 16), tonumber(value, 16))
                        console:log('write16: ' .. value .. ' to ' .. real_address)
                    else
                        console:log('Full address: ' .. real_address)
                        emu:write8(tonumber(real_address, 16), tonumber(value, 16))
                    end
                end
            end
        end
    end)
end)

console:log('mGBA socket server started on port 8888')