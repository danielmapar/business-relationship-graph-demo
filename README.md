# Graph Service Demo

This is the setup repository for a demo Business Relationship Graph service. It contains a `Vagrantfile` with the VM setup for executing the platform-api service and platform-frontend UI.

The platform-api service is a simple API that allows you to create and query a business relationship graph. We are leveraging the [AGE](https://age.apache.org/) extension for PostgreSQL to store and query the graph. The platform-frontend is a simple UI that allows you to create and query the graph.

## Local Development

### Getting Started with VirtualBox

* For **Windows users only**:
    * Disable Hyper-V by running `bcdedit /set hypervisorlaunchtype off` as administrator.
    * Reboot your machine.

* Install [Virtual Box](https://www.virtualbox.org/wiki/Downloads) version `7.1`.

* Install [Vagrant](https://developer.hashicorp.com/vagrant/downloads).

* Run `vagrant up --provision`.

* Run `vagrant ssh` to get inside of it afterwards.

### Running services locally

* Navigate to `cd /home/vagrant/graph-demo/local-dev`.
* Run `docker-compose build --no-cache` to build the `Dockerfile` associated with each service.
* Run `docker-compose up -d` to run all services.
* Run `docker-compose logs -f -t` to fetch service logs in real-time.
  * Run `docker-compose restart platform-api` to restart a service.
* Services:
    * Database: `localhost:5432`
      * Username: `demo`
      * Password: `password`
        * Intefacing with the database: `docker exec -it c4a9673fe15f psql -d platform_api_db -U demo`
    * Platform API: `localhost:8080`
      * [Postman Collection](./platform-api/Demo.postman_collection.json)
    * Platform Frontend: `localhost:3000`
    
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
