%define dbus_version            0.61
%define packagekit_version      0.2.3-3.20080611
%define alphatag                20080611

Summary:   GNOME PackageKit Client
Name:      gnome-packagekit
Version:   0.2.3
Release:   3.%{?alphatag}%{?dist}
License:   GPLv2+
Group:     Applications/System
URL:       http://www.packagekit.org
Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}-%{?alphatag}.tar.gz
Source1:   system-install-packages
Source2:   system-install-packages.1.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Patch0:    gnome-packagekit-enable-kde.patch
Requires:  gtk2 >= 2.12.0
Requires:  gnome-icon-theme
Requires:  libnotify >= 0.4.3
Requires:  unique >= 0.9.4
Requires:  dbus-glib >= %{dbus_version}
Requires:  dbus-x11 >= %{dbus_version}
Requires:  PackageKit >= %{packagekit_version}
Requires:  PackageKit-libs >= %{packagekit_version}
Requires:  shared-mime-info
Requires(post):   scrollkeeper
Requires(pre):    GConf2
Requires(post):   GConf2
Requires(preun):  GConf2
Requires(postun): scrollkeeper
Obsoletes: pirut < 1.3.30-3 
Provides:  pirut = 1.3.30-3

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
BuildRequires: gnome-doc-utils
BuildRequires: libsexy-devel
BuildRequires: PackageKit-devel >= %{packagekit_version}
BuildRequires: PolicyKit-gnome-devel
BuildRequires: unique-devel
BuildRequires: intltool

%description
packagekit-gnome provides session applications for the PackageKit API.
There are several utilities designed for installing, updating and
removing packages on your system.

%prep
%setup -q -n %{name}-%{version}-%{?alphatag}
%patch0 -p1

%build
%configure --disable-scrollkeeper --disable-schemas-install
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

install %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/system-install-packages
install -m 0644 -D %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/man/man1/system-install-packages.1.gz

desktop-file-install --delete-original                   \
  --dir=$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/                    \
  $RPM_BUILD_ROOT%{_datadir}/gnome/autostart/gpk-update-icon.desktop

for i in gpk-application gpk-update-viewer gpk-install-file gpk-log gpk-prefs gpk-repo ; do
  desktop-file-install --delete-original                                \
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
update-desktop-database %{_datadir}/applications
update-mime-database %{_datadir}/mime

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
update-desktop-database %{_datadir}/applications
update-mime-database %{_datadir}/mime

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%{_bindir}/gpk-*
%{_bindir}/system-install-packages
%{_datadir}/gnome-packagekit
%{_datadir}/icons/hicolor/16x16/status/*.png
%{_datadir}/icons/hicolor/22x22/status/*.png
%{_datadir}/icons/hicolor/24x24/status/*.png
%{_datadir}/icons/hicolor/48x48/status/*.png
%{_datadir}/icons/hicolor/scalable/status/*.svg
%config(noreplace) %{_sysconfdir}/gconf/schemas/*.schemas
%{_datadir}/man/man1/*.1.gz
%{_datadir}/gnome/help/gnome-packagekit
%{_datadir}/omf/gnome-packagekit
%{_sysconfdir}/xdg/autostart/gpk-update-icon.desktop
%{_datadir}/applications/gpk-*.desktop

%changelog
* Mon Jun 11 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-3.20080611
- Pull in a new snapshot from the unstable branch.
- New interface for gpk-application - one that doesn't suck
- UI fixes for gpk-repo and gpk-update-viewer

* Mon Jun 09 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-2.20080609
- Add intltool to the BR.

* Mon Jun 09 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-1.20080609
- Pull in a new snapshot from the unstable branch.

* Thu May 29 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.2-2.20080529
- Pull in a new snapshot from the unstable branch.

* Mon May 19 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.2-1.20080519
- Pull in a new snapshot from the unstable branch.

* Fri May 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.1-3.20080508
- Add a BR on unique to make the client tools single instance

* Thu May 08 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.1-2.20080508
- Pull in a new snapshot from the unstable branch.

* Tue May 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.1-1.20080506
- Pull in a new snapshot from the unstable branch.

* Tue May 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.0-1
- Update to the latest _UNSTABLE_ upstream source

* Sat Apr 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-5.20080416git
- Build against the right version of PackageKit to make koji DTRT.

* Sat Apr 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-4.20080416git
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes rh#442398.

* Sat Apr 15 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-3.20080415git
- Add a man page for system-install-packages. Fixes rh#441673

* Sat Apr 15 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-2.20080415git
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes include rh#442150, rh#442543, rh#442230, rh#441062 and more from upstream.

* Sat Apr 12 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-1.20080412git
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes that were cherry picked into this branch since 0.1.11 was released can be viewed at:
  http://gitweb.freedesktop.org/?p=users/hughsient/gnome-packagekit.git;a=log;h=GNOME_PACKAGEKIT_0_1_X

* Fri Apr 11 2008 Jesse Keating <jkeating@redhat.com> - 0.1.11-5
- Obsolete / Provide pirut.

* Thu Apr 10 2008 Owen Taylor <otaylor@redhat.com> - 0.1.11-4
- Make system-install-packages a wrapper script not a symlink
  so both files and package names work (#441674)

* Sat Apr  9 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.11-3
- Pull in the new icons from upsteam from Mike Langlie.

* Sat Apr  9 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.11-2
- Fix a plethora of GUI bugs by pulling some fixes from upstream

* Sat Apr  5 2008 Matthias Clasen  <mclasen@redhat.com> - 0.1.11-1
- Update to 0.1.11

* Fri Mar 28 2008 Bill Nottingham <notting@redhat.com> - 0.1.10-1
- update to 0.1.10
- add PK-gnome-devel build requirement

* Tue Mar 18 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-4
- move pk-update-icon.desktop to /etc/xdg/autostart/

* Thu Mar 13 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-3
- symlink pk-install-file to system-install-packages

* Tue Mar 11 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-2
- Apply patch to enable gnome-packagekit in KDE

* Wed Mar  5 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.9-1
- Update to latest upstream version: 0.1.8

* Thu Feb 21 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.8-1
- Update to latest upstream version: 0.1.8

* Fri Feb 15 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.7-1
- Update to latest upstream version: 0.1.7

* Sat Jan 19 2008 Robin Norwood <rnorwood@redhat.com> - 0.1.6-1
- Update to latest upstream version: 0.1.6

* Sun Dec 30 2007 Christopher Aillon <caillon@redhat.com> - 0.1.5-2
- Fix the build

* Fri Dec 21 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.5-1
- Update to latest upstream version: 0.1.5
 
* Tue Nov 27 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.4-1
- Update to latest upstream version: 0.1.4

* Mon Nov 12 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.3-1
- Update to latest upstream version: 0.1.3

* Sun Nov 11 2007 Ray Strode <rstrode@redhat.com> - 0.1.2-2
- remove --vendor "gnome" from desktop-file-install calls. It's
  deprecated and changes the latest of .desktop files.

* Thu Nov 01 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.2-1
- Update to latest upstream version: 0.1.2

* Tue Oct 23 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.1-1
- Update to latest upstream version

* Tue Oct 16 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.0-2
- Apply recommended fixes from package review
 
* Mon Oct 15 2007 Robin Norwood <rnorwood@redhat.com> - 0.1.0-1
- Initial build (based upon spec file from Richard Hughes)
