cd mix_scripts
python3 runmix1.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix1 &
python3 runmix2.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix2 &
python3 runmix3.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix3 &
python3 runmix4.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix4 &
python3 runmix5.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix5 
python3 runmix6.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix6 &
python3 runmix7.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix7 &
python3 runmix8.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix8 &
python3 runmix9.py input/7domains_8banks_8ranks_addressmapping2.cfg  output/mix9 &
python3 runmix10.py input/7domains_8banks_8ranks_addressmapping2.cfg output/mix10

cd ..
python3 graph_mix.py #fig 9