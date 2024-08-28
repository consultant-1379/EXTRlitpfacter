%define debug_package %{nil}

# VERSION is subbed out during rake srpm process
%global realversion 2.4.6
%global rpmversion <rpm.version>
%global packager <ericsson.rstate>
%global realname facter

# Fedora 17 ships with ruby 1.9, RHEL 7 with ruby 2.0, which use vendorlibdir instead
# of sitelibdir
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7
%global facter_libdir   %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["vendorlibdir"]')
%else
%global facter_libdir   %(ruby -rrbconfig -e 'puts RbConfig::CONFIG["sitelibdir"]')
%endif


Summary:        Ruby module for collecting simple facts about a host operating system
Name:           EXTRlitpfacter_CXP9031032
Version:        %{rpmversion}
Release:        1
License:        ASL 2.0
Group:          System Environment/Base
URL:            http://www.ericsson.com/
Source0:        http://puppetlabs.com/downloads/%{realname}/%{realname}-%{realversion}.tar.gz

BuildRoot:      %{_tmppath}/%{realname}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       ruby >= 1.8.7
Requires:       which
# dmidecode and pciutils are not available on all arches
%ifarch %ix86 x86_64 ia64
Requires:       dmidecode
Requires:       pciutils
%endif
Requires:       virt-what
# In Fedora 19+ or RHEL 7+ net-tools is required for interface facts
%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
Requires:       net-tools
%endif

Packager:       %{packager}
Provides:       facter = 1:%{realversion}

%description
Ruby module for collecting simple facts about a host Operating
system. Some of the facts are preconfigured, such as the hostname and the
operating system. Additional facts can be added through simple Ruby scripts
repackaged by Ericsson from PuppetLabs source code.

%prep
%setup -q  -n %{realname}-%{realversion}

%build

%install
rm -rf %{buildroot}
ruby install.rb --destdir=%{buildroot} --quick --sitelibdir=%{facter_libdir}
rm -rf %{buildroot}%{_mandir}/man8/facter.8.gz

%clean
rm -rf %{buildroot}

%post
SYSTEMCTL=/usr/bin/systemctl

if [ "$1" = "2" ] ; then
    chk_state=$("${SYSTEMCTL}" status puppet.service | grep Loaded | awk -F ';' '{print $2}' | tr -d '[:space:]');
    if [ "${chk_state}" == "enabled" ]
    then
        "${SYSTEMCTL}" stop puppet.service
        "${SYSTEMCTL}" start puppet.service || :
    fi
fi

%files
%defattr(-,root,root,-)
%{_bindir}/facter
%{facter_libdir}/facter.rb
%{facter_libdir}/facter
%doc LICENSE README.md

