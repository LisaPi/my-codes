#!/bin/bash

ntpdate time.nist.gov


HOME=/tmp/home/root

apt-get update
apt-get -y install gcc make libpcre3-dev 

# Install lighttpd from source.
# Madehsmall changes to the source code so that lighttpd would run as root (
# which is a must to eval ovs-ofctl commands).
tar xzf lighttpd-rootuid.tar.gz
cd lighttpd-1.4.31
./configure --without-bzip2 --without-zlib
make
make install
cd ../

# Copy the lighttpd configuration files into place
mkdir -p /etc/lighttpd
mkdir -p /var/log/lighttpd
tar xzf lighttpd.conf.tar.gz -C /etc/lighttpd

tar xzf oms.tar.gz
IP=`/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`
sed -i -r -e "s/10.10.50.[0-9]{3}/$IP/g" backend/oms.conf

#
# Install python modules including simplejson, flup, web.py and setuptools
#
cd $HOME
# module simplejson
if [ ! -f "simplejson-3.3.1.tar.gz" ]
then
    wget --no-check-certificate https://pypi.python.org/packages/source/s/simplejson/simplejson-3.3.1.tar.gz
fi
tar xzf simplejson-3.3.1.tar.gz
cd simplejson-3.3.1
python  setup.py install

cd $HOME
# module setuptools
if [ ! -f "setuptools-1.4.2.tar.gz" ]
then
    wget --no-check-certificate https://pypi.python.org/packages/source/s/setuptools/setuptools-1.4.2.tar.gz#md5=13951be6711438073fbe50843e7f141f
fi
tar xzf setuptools-1.4.2.tar.gz
cd setuptools-1.4.2
python  setup.py install

cd $HOME
# module web.py
if [ ! -f "web.py-0.37.tar.gz" ]
then
    wget http://webpy.org/static/web.py-0.37.tar.gz
fi
tar xzf web.py-0.37.tar.gz
cd web.py-0.37
python  setup.py install

cd $HOME
# module flup
if [ ! -f "flup-1.0.3.dev-20110405.tar.gz" ]
then
    wget --no-check-certificate https://pypi.python.org/packages/source/f/flup/flup-1.0.3.dev-20110405.tar.gz#md5=a005b072d144fc0e44b0fa4c5a9ba029
fi
tar xzf flup-1.0.3.dev-20110405.tar.gz
cd flup-1.0.3.dev-20110405
python setup.py install

pkill lighttpd
/usr/local/sbin/lighttpd -f /etc/lighttpd/lighttpd.conf
