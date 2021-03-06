%global origname RDPMux

%global _dbus_conf_dir %{_sysconfdir}/dbus-1/system.d

Name:           rdpmux
Version:        0.4.0
Release:        1%{?dist}
Summary:        RDP server multiplexer designed to work with virtual machines
License:        ASL 2.0
URL:            https://github.com/datto/RDPMux

Source0:        https://github.com/datto/%{origname}/archive/v%{version}/%{origname}-%{version}.tar.gz

%if 0%{?rhel} == 7
BuildRequires:  cmake3 >= 3.2
%else
BuildRequires:  cmake >= 3.2
%endif
BuildRequires:  freerdp-devel >= 2.0
BuildRequires:  glib2-devel
BuildRequires:  glibmm24-devel
BuildRequires:  msgpack-devel
BuildRequires:  boost-devel
BuildRequires:  pixman-devel
BuildRequires:  libsigc++20-devel
BuildRequires:  zeromq-devel >= 4.1.0

Requires(post):   openssl
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
RDPMux provides multiplexed RDP servers for virtual machines.

It communicates with VMs via librdpmux, which implements the
communication protocol and exposes an API for hypervisors to hook into.

%prep
%setup -qn %{origname}-%{version}

%build
%if 0%{?rhel} == 7
%cmake3 .
%else
%cmake .
%endif

%make_build V=1

%install
%make_install
mkdir -p %{buildroot}%{_unitdir}
install -pm 0644 dist/rdpmux.service %{buildroot}%{_unitdir}
mkdir -p %{buildroot}%{_dbus_conf_dir}
install -pm 0644 dist/org.RDPMux.RDPMux.conf %{buildroot}%{_dbus_conf_dir}

# Setting up files for ghost file list directive
# See: http://www.rpm.org/max-rpm-snapshot/s1-rpm-inside-files-list-directives.html
mkdir -p %{buildroot}%{_sharedstatedir}/rdpmux
touch %{buildroot}%{_sharedstatedir}/rdpmux/server.key
touch %{buildroot}%{_sharedstatedir}/rdpmux/server.crt

%post
if [ "$1" = "1" ]; then
    if [ ! -e "/var/lib/rdpmux/server.key" ]; then
        mkdir -p %{_sharedstatedir}/rdpmux
        openssl req -x509 -newkey rsa:2048 -keyout %{_sharedstatedir}/rdpmux/server.key -out %{_sharedstatedir}/rdpmux/server.crt -nodes -subj "/C=US"
    fi
fi
%systemd_post rdpmux.service

%preun
%systemd_preun rdpmux.service

%postun
%systemd_postun_with_restart rdpmux.service

%files
%{_bindir}/rdpmux
%{_unitdir}/rdpmux.service
%{_dbus_conf_dir}/org.RDPMux.RDPMux.conf
%license LICENSE
%ghost %{_sharedstatedir}/rdpmux
%ghost %{_sharedstatedir}/rdpmux/server.key
%ghost %{_sharedstatedir}/rdpmux/server.crt

%changelog
* Tue Jul 12 2016 Neal Gompa <ngompa@datto.com> - 0.4.0-1
- Bump to 0.4.0

* Thu May 26 2016 Neal Gompa <ngompa@datto.com> - 0.2.4-1
- Bump to 0.2.4

* Tue May 24 2016 Neal Gompa <ngompa@datto.com> - 0.2.2-1
- Bump to 0.2.2

* Tue May 24 2016 Anthony Gargiulo <agargiulo@datto.com> - 0.2.1-1
- Added DBus conf and systemd service files
- Changed file and directory permissions to 777

* Tue May 17 2016 Sri Ramanujam <sramanujam@datto.com> - 0.2.0-1
- New DBus registration protocol

* Fri Apr 29 2016 Sri Ramanujam <sramanujam@datto.com> - 0.1.2-1
- Initial packaging
