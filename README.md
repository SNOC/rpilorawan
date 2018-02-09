# rpilorawan board control script

##### Aim of this script is to control the rpilorawan board to send messages on the LoraWan network.

The expansion board is for raspberry pi mainboard and allows sending messages over the [LoraWan network](https://www.lora-alliance.org/)

You can purchase the board on [YADOM.FR](https://yadom.fr/reseaux-iot/lorawan/kit-carte-de-communication-lorawan-pour-raspberry-pi.html).

This python script allows :
- reading preprogrammed EUI
- joining a network using OTAA or ABP
- sending data with or without requesting a response

# Usage
## reading preprogrammed EUI
```bash
python sendlorawan.py --eui
```

## joining an OTAA Lora network providing devEUI (0004A30B001EBA62) appEUI (0000000000000001) and appKey (4E2086153FB762C2E079A1F791792400) and sending frame 0A1B
```bash
python sendlorawan.py --otaa 0004A30B001EBA62 0000000000000001 4E2086153FB762C2E079A1F791792400 --send 0A1B
```

## joining an OTAA Lora network providing devEUI (0004A30B001EBA62) appEUI (0000000000000001) and appKey (4E2086153FB762C2E079A1F791792400) and sending frames A4B5 and then FCD45E0C expecting a downlink frame
```bash
python sendlorawan.py --otaa 0004A30B001EBA62 0000000000000001 4E2086153FB762C2E079A1F791792400
python sendlorawan.py --send A4B5
python sendlorawan.py --send FCD45E0C --receive
```

## joining an ABP Lora network providing NwkSkey () AppSKey () and devAddr () and sending frame AB50
```bash
python sendlorawan.py --abp    --send AB50
```

## Notes
Short arguments are supported (ie -p for --port)
The serial port path can be specified with option ```--port```, default is ```/dev/ttyAMA0```
The Lora channel can be specified when sending with option ```--channel```, default is ```1```

# Prerequistes
*The following steps should be performed in the following order*
1. Disable Raspberry Pi terminal on serial port with raspi-config utility:
    ```bash
    sudo raspi-config
    ```
    Go to ```Interfacing Options``` then choose ```Serial``` then ```NO``` and ```OK```

2. Install pyserial
    ```bash
    sudo apt-get install python-serial
    ```

3. Download scripts
    - if git is installed then clone the repository :
    ```bash
    git clone https://github.com/SNOC/rpilorawan.git
    ```
    - otherwise paste script content to a new file:
    ```bash
    nano sendlorawan.py
    ```

4. Plug antenna with its cable and test the communication:
    ```bash
    python sendlorawan.py --eui
    ```

### Pi3 specific requirements
1. Edit ```/boot/config.txt```
      ```bash
      sudo nano /boot/config.txt
      ```
   1. disable if present ```dtoverlay=pi3-miniuart-bt``` by adding ```#``` character at line begining :
   ```#dtoverlay=pi3-miniuart-bt```
   2. if not present, add :
        ```bash
        dtoverlay=pi3-disable-bt
        enable_uart=1
        ```
        *note: ```enable_uart=0``` might be present at the end of the file, in such case it should be commented or modified to ```enable_uart=1```*

2. then reboot :
    ```bash
    sudo reboot
    ```
Serial port to use is the script's default one : ```/dev/ttyAMA0```

##### License

MIT License / read license.txt
