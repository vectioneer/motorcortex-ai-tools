# Getting started

Pages under https://docs.motorcortex.io/docs/getting-started/ — captured 2026-10-28 from the sitemap.
Each entry: page title (link) — the page's own description.

Go from an empty controller to a running Motorcortex application you can see and control, in four steps and without any machine hardware.

- [Connect your PC](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/) — Put your PC on the controller's network and make your browser trust it, so the Motorcortex tools can reach the controller.
  - [Configure your network](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/configure-your-network/) — Give your PC a fixed address on the controller's network and check that it can reach the controller.
    - [Configure your network on macOS](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/configure-your-network/macos/) — Set a fixed address on the wired network port of a Mac.
    - [Configure your network on Ubuntu](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/configure-your-network/ubuntu/) — Set a fixed address on the wired network port of an Ubuntu PC.
    - [Configure your network on Windows](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/configure-your-network/windows/) — Set a fixed address on the wired network adapter of a Windows PC.
  - [Connection troubleshooting](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/connection-troubleshooting/) — Find out why your PC cannot reach the controller or its application, one check at a time.
  - [Install a browser certificate](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/) — Make your browser trust the controller, so the Motorcortex tools can open an encrypted connection to it.
    - [Check the certificate in Chrome](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/check-chrome/) — What Chrome shows when the certificate works, and when it does not.
    - [Check the certificate in Firefox](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/check-firefox/) — What Firefox shows when the certificate works, and when it does not.
    - [Install the certificate in Firefox](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/firefox/) — Import the Motorcortex Root CA into the certificate authorities of Firefox.
    - [Install the certificate on macOS](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/macos/) — Add the Motorcortex Root CA to Keychain Access on macOS and trust it.
    - [Install the certificate in Chrome on Ubuntu](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/ubuntu/) — Import the Motorcortex Root CA into the trusted certificates of Chrome on Ubuntu.
    - [Install the certificate on Windows](https://docs.motorcortex.io/docs/getting-started/connect-your-pc/install-a-browser-certificate/windows/) — Import the Motorcortex Root CA into the Windows store of trusted root certificates.
- [Deploy an application](https://docs.motorcortex.io/docs/getting-started/deploy-app/) — Copy an application from the motorcortex.io store into a project and deploy its three packages to your controller.
- [Set up a controller](https://docs.motorcortex.io/docs/getting-started/install-mcxos/) — Install MCX-RTOS on an industrial PC, a Raspberry Pi or a virtual machine, or create a cloud machine that already runs it.
  - [Use a cloud machine](https://docs.motorcortex.io/docs/getting-started/install-mcxos/cloud-machine/) — Create a virtual machine on motorcortex.io that runs MCX-RTOS in the cloud, so you need no controller, no install and no network cable.
  - [Install MCX-RTOS](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/) — Put MCX-RTOS, the operating system that runs Motorcortex, on an industrial PC, a Raspberry Pi or a virtual machine on your own PC.
    - [Download](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/download/)
      - [Industrial PC](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/download/intel/) — Download the Intel image and the imager stick image for an industrial PC.
      - [Raspberry Pi](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/download/rpi4/) — Download the Raspberry Pi image of MCX-RTOS.
      - [Virtual machine](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/download/virtualmachine-intel/) — Download the MCX-RTOS image for a virtual machine in QEMU or VirtualBox.
    - [Install](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/) — Choose how to install the MCX-RTOS image, depending on your controller.
      - [Install on a Raspberry Pi](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/sdcard/) — Write the MCX-RTOS image to an SD card for a Raspberry Pi and connect to it.
        - [Install on a Raspberry Pi Compute Module](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/sdcard/rpi-compute-module-install/) — Write the MCX-RTOS image to the built-in storage of a Raspberry Pi 4 Compute Module over USB.
      - [Install on an industrial PC](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/) — Create a USB imager stick and use it to install MCX-RTOS on the disk of an industrial PC.
        - [Back up the controller with mci backup](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/backup/) — A backup saves the controller’s disk as an image on the stick, so you can install it again later with mci restore. Make sure the stick has …
        - [Open the imager terminal with a keyboard and display](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/connect-disp/) — Connect a keyboard and a display to the controller. After the stick has booted, the display shows the imager terminal, ready for a command. If it asks …
        - [Open the imager terminal over SSH](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/connect-ssh/) — With SSHSSH (Secure Shell) opens a terminal on another computer over the network. Ubuntu, macOS and Windows 10 and later have the ssh command built …
        - [Install the image with mci restore](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/restore/) — Warning Installing the image erases everything on the disk you choose. Back up the controller first if you want to keep its current …
        - [Create the imager stick on Ubuntu](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/ubuntu/) — Ubuntu writes the image with its Disks tool, through Disk Image Writer. In your file manager, right-click the imager stick image ( …
        - [Create the imager stick on Windows](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/usb/windows/) — Windows has no built-in tool to write a disk image, so you use a separate one such as Rufus. Install and start the disk image writer. Select your …
      - [Run a virtual machine](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/virtual-machine/) — Run MCX-RTOS as a virtual machine on your own PC, in QEMU on Ubuntu or in VirtualBox.
        - [Run MCX-RTOS in QEMU on Ubuntu](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/virtual-machine/ubuntu-qemu/) — Start the MCX-RTOS Intel disk image in QEMU on Ubuntu, with a network bridge to your PC.
        - [Run MCX-RTOS in VirtualBox on Ubuntu](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/virtual-machine/ubuntu/) — Install VirtualBox on Ubuntu, set up its host-only network and import the Motorcortex appliance.
        - [Run MCX-RTOS in VirtualBox on Windows](https://docs.motorcortex.io/docs/getting-started/install-mcxos/install-rtos/install/virtual-machine/windows/) — Install VirtualBox on Windows, set up its host-only network and import the Motorcortex appliance.
- [Log in to motorcortex.io](https://docs.motorcortex.io/docs/getting-started/login-mcx-io/) — The log-in step shared by the Getting started pages.
- [Play](https://docs.motorcortex.io/docs/getting-started/play/) — Read and change the live values of your application in Motorcortex Desk, and build your own dashboard for it in Motorcortex Grid.
  - [Create a GUI](https://docs.motorcortex.io/docs/getting-started/play/create-gui/) — Build a small dashboard in Motorcortex Grid with a switch and a light, test it live, and deploy it to your controller.
  - [Use Motorcortex Desk](https://docs.motorcortex.io/docs/getting-started/play/use-motorcortex-desk/) — Connect Motorcortex Desk to your controller, find a parameter, write a value and plot it live.
