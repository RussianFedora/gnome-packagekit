%define dbus_version            0.61
%define packagekit_version      0.2.3

Summary:   GNOME PackageKit Client
Name:      gnome-packagekit
Version:   0.2.4
Release:   2%{?dist}
License:   GPLv2+
Group:     Applications/System
URL:       http://www.packagekit.org
#Source0:   http://people.freedesktop.org/~hughsient/releases/%{name}-%{version}-%{?alphatag}.tar.gz
Source0:   http://www.packagekit.org/releases/%{name}-%{version}.tar.gz
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
%setup -q
#%setup -q -n %{name}-%{version}-%{?alphatag}
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
update-desktop-database %{_datadir}/applications &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

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
update-desktop-database %{_datadir}/applications &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

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
* Mon Aug 04 2008 Robin Norwood <rnorwood@redhat.com> - 0.2.4-2
- Fix Source0 URL.

* Tue Jul 31 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.4-1
- New upstream version, only bugfixes.

* Thu Jul 31 2008 Robin Norwood <rnorwood@redhat.com> - 0.2.3-9
- Re-apply the gnome-packagekit-enable-kde patch
- rhbz#437048

* Mon Jul 28 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-8
- Silence output of update-desktop-database and update-mime-database

* Mon Jul 21 2008 Adel Gadllah <adel.gadllah@gmail.com> - 0.2.3-7
- Rebuild against new PackageKit to pick up correct dep

* Tue Jul 15 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-6
- Add intltool to the BR.

* Tue Jul 15 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-5
- Correct the name of the executables called in system-install-packages.
  Fixes rh#455390

* Tue Jul 08 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-4
- Set the GUI interaction mode in the gpk-install-foo tools
  so the dialog does not auto-close when we've asked for auth.

* Fri Jul 04 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-3
- Fix the .. release string.

* Fri Jul 04 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-2
- Require PackageKit 0.2.3 to keep koji happy.

* Fri Jul 04 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-1
- New upstream stable version (API break from 0.1.12).
 * UI fixes and new functionality
 * Multiple actions in one transaction
- Fixes many bugs with the 0.1.x codebase.

* Mon May 19 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-14.20080516
- Prevent the GTK GUI tools from being run as root as PolicyKit authentication
  will not work, and using GTK in this way so may be insecure.
- This will also reduce to zero the number of bugs I'm getting about the gpk-*
  tools not working when logged into as the root account.
  Addresses: #447266, #446440 and a ton of duplicates!

* Fri May 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-13.20080516
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes rh#446739, where we make the visited link status in gpk-update-viewer only mark the
  correct URI as visited, rather than all of them. 

* Fri May 02 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-12.20080430
- Add some more stuff to the GPG patch to fix point 3) of rh#444826

* Wed Apr 30 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-11.20080430
- Actually build the correct tarball so the patches apply.

* Wed Apr 30 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-10.20080430
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes rh#442223, which is a release blocker.

* Wed Apr 30 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-9.20080430
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- Fixes rh#441755, which is a release blocker.

* Wed Apr 30 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-8.20080423
- Bodge in some of the GPG import code from master in an attempt to be able to
  install signatures for F9.
- Fixes rh#443445, which is a release blocker.

* Sat Apr 23 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-7.20080423
- Pull in the new snapshot from the stable GNOME_PACKAGEKIT_0_1_X branch.
- rh#443210, rh#438624, rh#436726, rh#443117, rh#442647 and rh#442998.

* Wed Apr 23 2008 Richard Hughes  <rhughes@redhat.com> - 0.1.12-6.20080416git
- Correct the permissions on a man page to fix rh#443175.

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
