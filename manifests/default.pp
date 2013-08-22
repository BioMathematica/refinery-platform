$appuser = "vagrant"
$virtualenv = "/home/${appuser}/.virtualenvs/refinery-platform"
$venvpath = "${virtualenv}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/opt/vagrant_ruby/bin"
$requirements = "/vagrant/requirements.txt"
$project_root = "/vagrant/refinery"

#TODO: peg packages to specific versions
class venvdeps {
  package { 'build-essential': }
  package { 'libncurses5-dev': }
  package { 'libfreetype6': }      # required by matplotlib
  package { 'libfreetype6-dev': }  # required by matplotlib
  package { 'libpng12-dev': }      # required by matplotlib
  package { 'libldap2-dev': }
  package { 'libsasl2-dev': }
  package { 'postgresql-server-dev-all': }
}
include venvdeps

package { 'postgresql': }
package { 'openjdk-7-jre': }  # required by solr
package { 'curl': }  # required by rabbitmq installer
package { 'virtualenvwrapper': }

class { 'postgresql':
  charset => 'UTF8',
  locale => 'en_US.utf8',
}
->
class { 'postgresql::server':
}
postgresql::db { 'refinery':
  user => $appuser,
  password => '',
}

class { 'python':
  version => 'system',
  pip => true,
  dev => true,
  virtualenv => true,
}
# create virtualenv
python::virtualenv { $virtualenv:
  ensure => present,
  #requirements => $requirements,  # creates a dependency cycle
  owner => $appuser,
  group => $appuser,
}
->
# a workaround for a bug in matplotlib installation
# python::pip doesn't work because it creates a dependency cycle
exec { "numpy":
  command => "pip install numpy==1.7.0",
  path => $venvpath,
  user => $appuser,
  group => $appuser,
  require => Class["venvdeps"],
}
~>
# install packages from requirements.txt
python::requirements { $requirements:
  virtualenv => $virtualenv,
  owner => 'vagrant',
  group => 'vagrant',
}

file { [ "/vagrant/media", "/vagrant/static", "/vagrant/isa-tab" ]:
  ensure => directory,
  owner => $appuser,
  group => $appuser,
}

exec { "syncdb":
  command => "${project_root}/manage.py syncdb --noinput --all",
  path => $venvpath,
  user => $appuser,
  group => $appuser,
  require => [
               File["/vagrant/media"],
               Python::Requirements[$requirements],
               Postgresql::Db["refinery"]
             ],
}
->
exec { "migrate":
  command => "${project_root}/manage.py migrate",
  path => $venvpath,
  user => $appuser,
  group => $appuser,
}
->
exec { "init_refinery":
  command => "${project_root}/manage.py init_refinery 'Refinery' 'localhost:8000'",
  path => $venvpath,
  user => $appuser,
  group => $appuser,
}
->
exec {
  "build_core_schema":
    command => "${project_root}/manage.py build_solr_schema --using=core > solr/core/conf/schema.xml",
    cwd => $project_root,
    path => $venvpath,
    user => $appuser,
    group => $appuser;
  "build_data_set_manager_schema":
    command => "${project_root}/manage.py build_solr_schema --using=data_set_manager > solr/data_set_manager/conf/schema.xml",
    cwd => $project_root,
    path => $venvpath,
    user => $appuser,
    group => $appuser;
}

$solr_version = "4.4.0"
$solr_archive = "solr-${solr_version}.tgz"
$solr_url = "http://mirror.cc.columbia.edu/pub/software/apache/lucene/solr/${solr_version}/${solr_archive}"
exec { "solr_wget":
  command => "wget ${solr_url} -O /usr/src/${solr_archive}",
  creates => "/usr/src/${solr_archive}",
  path => "/usr/bin:/bin",
}
->
exec { "solr_unpack":
  command => "mkdir -p /opt && tar -xzf /usr/src/${solr_archive} -C /opt && chown -R ${appuser}:${appuser} /opt/solr-${solr_version}",
  creates => "/opt/solr-${solr_version}",
  path => "/usr/bin:/bin",
}
->
file { "/opt/solr":
  ensure => link,
  target => "solr-${solr_version}",
}

# configure rabbitmq
class { '::rabbitmq':
  package_ensure => installed,
  service_ensure => running,
  port => '5672',
  require => Package['curl'],
}
rabbitmq_user { 'guest':
  password => 'guest',
  require => Class['::rabbitmq'],
}
rabbitmq_vhost { 'localhost':
  ensure => present,
  require => Class['::rabbitmq'],
}
rabbitmq_user_permissions { 'guest@localhost':
  configure_permission => '.*',
  read_permission => '.*',
  write_permission => '.*',
  require => [ Rabbitmq_user['guest'], Rabbitmq_vhost['localhost'] ]
}

file { "${project_root}/supervisord.conf":
  ensure => file,
  source => "${project_root}/supervisord.conf.sample",
  owner => $appuser,
  group => $appuser,
}
