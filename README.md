# Local Development

This is the setup repository for the Intuit system design exercise. It contains a `Vagrantfile` with the VM setup for executing the platform-api service.

### Getting Started with VirtualBox

* For **Windows users only**:
    * Disable Hyper-V by running `bcdedit /set hypervisorlaunchtype off` as administrator.
    * Reboot your machine.

* Install [Virtual Box](https://www.virtualbox.org/wiki/Downloads) version `7.1`.

* Install [Vagrant](https://developer.hashicorp.com/vagrant/downloads).

* Run `vagrant up --provision`.

* Run `vagrant ssh` to get inside of it afterwards.

### Running services locally

* Navigate to `cd /home/vagrant/interview-intuit/local-dev`.
* Run `docker-compose build --no-cache` to build the `Dockerfile` associated with each service.
* Run `docker-compose up -d` to run all services.
* Run `docker-compose logs -f -t` to fetch service logs in real-time.
  * Run `docker-compose restart platform-api` to restart a service.
* Services:
    * Database: `localhost:5432`
      * Username: `intuit`
      * Password: `password`
        * Intefacing with the database: `docker exec -it c4a9673fe15f psql -d platform_api_db -U intuit`

### Helpful commands

* Turn off the VM: `vagrant halt`
* Turn on the VM: `vagrant up`
* Turn provision VM resources: `vagrant up --provision`
* Destroy a VM: `vagrant destroy`
* Clean up all Docker images and containers: `docker system prune -a --volumes`
  * Clean up all volumes: `docker volume prune`

### Configuring Visual Code Remote

`Vagrant` does volume mapping between the VM and the host machine, but in case you want to use `VS Code` to edit files inside the VM,
you can follow these steps:

* Execute `vagrant ssh-config`.
* Add the configuration to your `~/.ssh/config` file.
* Install the VS Code `Remote - SSH` extension.
* Click on the extension menu and enjoy!