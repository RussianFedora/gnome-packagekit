%define dbus_version 0.61
%define packagekit_version       0.1.1

Summary:   GNOME PackageKit Client
Name:      gnome-packagekit
Version:   %{packagekit_version}
Release:   1%{?dist}
License:   GPLv2+
Group:     Applications/System
URL:       http://www.packagekit.org
Source0:   http://people.freedesktop.org/~hughsient/releases/gnome-packagekit-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:  gtk2 >= 2.10.0
Requires:  gnome-icon-theme
Requires:  libnotify >= 0.4.3
Requires:  dbus-glib >= %{dbus_version}
Requires:  dbus-x11 >= %{dbus_version}
Requires(post):   scrollkeeper
Requires(pre):    GConf2
Requires(post):   GConf2
Requires(preun):  GConf2
Requires(postun): scrollkeeper

BuildRequires: libgnomeui-devel
BuildRequires: libglade2-devel
BuildRequires: libwnck-devel
BuildRequires: dbus-devel >= %{dbus_version}
BuildRequires: libnotify-devel
BuildRequires: gnome-panel-devel
BuildRequires: scrollkeeper
BuildRequires: gnome-doc-utils >= 0.3.2
BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: libtool
BuildRequires: cairo-devel
BuildRequires: startup-notification-devel
BuildRequires: perl(XML::Parser)
BuildRequires: PackageKit-devel = %{packagekit_version}

%description
packagekit-gnome provides session applications for the PackageKit API.
There are several utilities designed for installing, updating and
removing packages on your system.

%prep
%setup -q

%build
%configure --disable-scrollkeeper
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

desktop-file-install --vendor="gnome" --delete-original                 \
  --dir=$RPM_BUILD_ROOT%{_datadir}/gnome/autostart                      \
  $RPM_BUILD_ROOT%{_datadir}/gnome/autostart/pk-update-icon.desktop

for i in pk-application pk-update-viewer pk-update-icon pk-install-file pk-transaction-viewer pk-prefs pk-repo ; do
  desktop-file-install --vendor="gnome" --delete-original               \
    --dir=$RPM_BUILD_ROOT%{_datadir}/applications/                      \
    $RPM_BUILD_ROOT%{_datadir}/applications/$i.desktop
done

%find_lang %name

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
        %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas >/dev/null || :
scrollkeeper-update -q
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi
/usr/bin/update-desktop-database %{_datadir}/applications

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas > /dev/null || :
fi

%postun
scrollkeeper-update -q
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q %{_datadir}/icons/hicolor
fi
/usr/bin/update-desktop-database %{_datadir}/applications

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%{_bindir}/pk-*
%{_datadir}/gnome-packagekit
%config(noreplace) %{_sysconfdir}/gconf/schemas/*.schemas
%{_datadir}/gnome/help/gnome-packagekit
%{_datadir}/omf/gnome-packagekit
%{_datadir}/gnome/autostart/gnome-pk-update-icon.desktop
%{_datadir}/applications/gnome-pk-*.desktop

%changelog
* Tue Oct 23 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.1-1
- Update to latest upstream version

* Tue Oct 16 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.0-2
- Apply recommended fixes from package review
 
* Mon Oct 15 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.0-1
- Initial build (based upon spec file from Richard Hughes)
