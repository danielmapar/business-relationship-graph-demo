# Local Development

This is the setup repository for the [Sigtunnel](https://github.com/sigtunnel) organization. It contains a `Vagrantfile` with the VM setup for 
local development.

### Getting Started with VirtualBox

* For **Windows users only**:
    * Disable Hyper-V by running `bcdedit /set hypervisorlaunchtype off` as administrator.
    * Reboot your machine.

* Install [Virtual Box](https://www.virtualbox.org/wiki/Downloads) version `7.1`.
  * Version `7.1` requires a [workaround](https://github.com/hashicorp/vagrant/issues/13501).

* Install [Vagrant](https://developer.hashicorp.com/vagrant/downloads).

* Install [vagrant-vbguest](https://github.com/dheerapat/vagrant-vbguest) with `Administrative` privileges.
  * ```bash
    choco install ruby
    cd ..
    git clone https://github.com/dheerapat/vagrant-vbguest.git
    cd vagrant-vbguest
    gem build vagrant-vbguest.gemspec
    # vagrant-vbguest plugin workaround for https://github.com/dotless-de/vagrant-vbguest/issues/332
    vagrant plugin install vagrant-vbguest-0.32.1.gem
    ```

* Run `vagrant up --provision`.

* For **Windows users only**:
  * Turn off the VM: `vagrant halt`
  * Enable Symbolic Links for the Virtual Machine:
      * Open a terminal as `Administrator`.
      * `cd 'C:\Program Files\Oracle\VirtualBox\'`
      * `.\VBoxManage setextradata VM_NAME VBoxInternal2/SharedFoldersEnableSymlinksCreate/SHARE_NAME 1`
        * Replace `VM_NAME` with the name of your VM.
          * `signtunnel` is the default name.
          * If you don't remember this, in Virtual Box go to `Machine > Settings > General > Basic > Name`.
        * Replace `SHARE_NAME` with the name of the shared folder.
          * `home_vagrant_sigtunnel` is the default name.
          * If you don't remember this, in Virtual Box go to `Machine > Settings > Shared Folders`.

### Getting Started with VMware Workstation Pro / VMware Fusion

* **[DISCLAIMER] This is unstable, with notorious issues with symlinks, git, and other tools.**
  * https://knowledge.broadcom.com/external/article?legacyId=1007277

* For **Windows users only**:
    * Disable Hyper-V by running `bcdedit /set hypervisorlaunchtype off` as administrator.
    * Reboot your machine.

* Install [VMware Workstation Pro](https://www.vmware.com/products/workstation-pro.html) for Windows or [VMware Fusion](https://www.vmware.com/products/fusion.html) for Mac.A step-by-step guide can be found [here](https://www.mikeroysoft.com/post/download-fusion-ws/).

* Install [Vagrant](https://developer.hashicorp.com/vagrant/downloads).

* Install [VMWare Utilities for Vagrant](https://developer.hashicorp.com/vagrant/install/vmware).

* Install VMWare Plugin for Vagrant: `vagrant plugin install vagrant-vmware-desktop`.

* Run `VAGRANT_DEFAULT_PROVIDER=vmware_desktop vagrant up --provision`.
    * This will build your development Virtual Machine.

* Run `vagrant ssh` to get inside of it after wards.

### Run services locally

* Navigate to `cd /home/vagrant/sigtunnel/local-dev`.
* Run `docker-compose build --no-cache` to build the `Dockerfile` associated with each service.
* Run `docker-compose up -d` to run all services.
* Run `docker-compose logs -f -t` to fetch service logs in real-time.
  * Run `docker-compose restart platform-frontend` to restart a service.
* Services:
    * Platform Web UI: `http://localhost:3000/`
      * Username: `admin@sigtunnel.com`
      * Password: `password`
    * Platform API: `http://localhost:8080/` or `http://localhost:5005/` for debugging
    * AWS Cognito: `http://localhost:9229/`
    * Database: `localhost:5432`
      * Username: `sigtunnel`
      * Password: `password`

### Helpful commands

* Turn off the VM: `vagrant halt`
* Turn on the VM: `vagrant up`
* Turn provision VM resources: `vagrant up --provision`
* Destroy a VM: `vagrant destroy`
* Clean up all Docker images and containers: `docker system prune -a --volumes`
  * Clean up all volumes: `docker volume rm $(docker volume ls -q)` or `docker volume prune`

### Configuring Visual Code Remote

`Vagrant` does volume mapping between the VM and the host machine, but in case you want to use `VS Code` to edit files inside the VM,
you can follow these steps:

* Execute `vagrant ssh-config`.
* Add the configuration to your `~/.ssh/config` file.
* Install the VS Code `Remote - SSH` extension.
* Click on the extension menu and enjoy!

### Text Editor Preferences

* VS Code or Cursor:
  * You can find editor preferences in the `./text-editor-preferences/.vscode` folder.
* IntelliJ:
  * You can find editor preferences in the `./text-editor-preferences/.idea` folder.
