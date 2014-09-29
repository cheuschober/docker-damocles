===============
Docker Damocles
===============

A daemon for killing long-running docker instances. This was created as an
external monitor to pair with Jenkins for long-running (likely infinite)
builds that Jenkins could not time-out on its own.

Installation
------------
#.  install deps

#.  Place ``docker-damocles`` in ``/etc/init.d/`` and chmod to 755

#.  Place ``docker_damocles.py`` in ``/usr/local/bin``

.. code:: console

    $ git clone https://github.com/cheuschober/docker-damocles.git
    $ sudo apt-get install python-pip
    $ sudo pip install docker-py logging python-daemon
    $ sudo cp docker-damocles/docker-damocles /etc/init.d/
    $ sudo dp docker-damocles/docker_damocles.py /usr/local/bin/
    $ sudo service docker-damocles start

Usage
-----

.. code:: console

    $ sudo service docker-damocles start
    $ sudo service docker-damocles restart
    $ sudo service docker-damocles stop

Warranty
--------

There is none. You're welcome to use and abuse this as you please. Notably, it
offers no external configuration outside of modifying ``docker_damocles.py``
itself but if you want to do so, it should be fairly trivial as it's still
rather DRY.
