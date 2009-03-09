%define dbus_version            0.61
%define packagekit_version      0.4.5

%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Summary:   Session applications to manage packages
Name:      gnome-packagekit
Version:   0.4.5
Release:   2%{?dist}
License:   GPLv2+
Group:     Applications/System
URL:       http://www.packagekit.org
Source0:   http://www.packagekit.org/releases/%{name}-%{version}.tar.gz
Source1:   system-install-packages
Source2:   system-install-packages.1.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Fedora-specific -- requires behdad's new fontconfig before it's useful
#Patch0:    gnome-packagekit-0.4.0-set-gtk-module-false.patch

# Fedora specific, as we want bleeding edge
Patch1:    gnome-packagekit-0.4.5-use-unfinished-update-viewer.patch

Requires:  gtk2 >= 2.12.0
Requires:  gnome-icon-theme
Requires:  libnotify >= 0.4.3
Requires:  unique >= 0.9.4
Requires:  dbus-glib >= %{dbus_version}
Requires:  dbus-x11 >= %{dbus_version}
Requires:  PackageKit >= %{packagekit_version}
Requires:  PackageKit-libs >= %{packagekit_version}
Requires:  PackageKit-gtk-module >= %{packagekit_version}
Requires:  shared-mime-info
Requires:  iso-codes
Requires(post):   scrollkeeper
Requires(pre):    GConf2
Requires(post):   GConf2
Requires(preun):  GConf2
Requires(postun): scrollkeeper
Obsoletes: pirut < 1.3.31-2
Provides:  pirut = 1.3.31-2

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
BuildRequires: gnome-menus-devel
BuildRequires: PackageKit-devel >= %{packagekit_version}
BuildRequires: PolicyKit-gnome-devel
BuildRequires: unique-devel
BuildRequires: intltool
BuildRequires: xorg-x11-proto-devel
BuildRequires: fontconfig-devel

%description
gnome-packagekit provides session applications for the PackageKit API.
There are several utilities designed for installing, updating and
removing packages on your system.

%package extra
Summary: Session applications to manage packages (extra bits)
Group: Applications/System
Requires: %{name} = %{version}-%{release}

%description extra
Extra GNOME applications for using PackageKit, for instance an advanced update
viewer and a service pack creator.

%prep
%setup -q
#%patch0 -p1
%patch1 -p1

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


# save space by linking identical images in translated docs
helpdir=$RPM_BUILD_ROOT%{_datadir}/gnome/help/%{name}
for f in $helpdir/C/figures/*.png; do
  b="$(basename $f)"
  for d in $helpdir/*; do 
    if [ -d "$d" -a "$d" != "$helpdir/C" ]; then
      g="$d/figures/$b"
      if [ -f "$g" ]; then
        if cmp -s $f $g; then
          rm "$g"; ln -s "../../C/figures/$b" "$g"
        fi  
      fi 
    fi 
  done
done

%find_lang %name

%clean
rm -rf $RPM_BUILD_ROOT

%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
        %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas >/dev/null || :
scrollkeeper-update -q &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q %{_datadir}/icons/hicolor &> /dev/null || :
fi
update-desktop-database %{_datadir}/applications &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas &> /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
      %{_sysconfdir}/gconf/schemas/gnome-packagekit.schemas &> /dev/null || :
fi

%postun
scrollkeeper-update -q &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q %{_datadir}/icons/hicolor &> /dev/null || :
fi
update-desktop-database %{_datadir}/applications &> /dev/null || :
update-mime-database %{_datadir}/mime &> /dev/null || :

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%{_bindir}/gpk-application
%{_bindir}/gpk-install-*
%{_bindir}/gpk-log
%{_bindir}/gpk-prefs
%{_bindir}/gpk-repo
%{_bindir}/gpk-update-icon
%{_bindir}/gpk-update-viewer
%{_bindir}/system-install-packages
%dir %{_datadir}/gnome-packagekit
%{_datadir}/gnome-packagekit/gpk-application.glade
%{_datadir}/gnome-packagekit/gpk-client.glade
%{_datadir}/gnome-packagekit/gpk-eula.glade
%{_datadir}/gnome-packagekit/gpk-prefs.glade
%{_datadir}/gnome-packagekit/gpk-update-viewer.glade
%{_datadir}/gnome-packagekit/gpk-error.glade
%{_datadir}/gnome-packagekit/gpk-log.glade
%{_datadir}/gnome-packagekit/gpk-repo.glade
%{_datadir}/gnome-packagekit/gpk-signature.glade
%dir %{_datadir}/gnome-packagekit/icons
%dir %{_datadir}/gnome-packagekit/icons/hicolor
%dir %{_datadir}/gnome-packagekit/icons/hicolor/*
%dir %{_datadir}/gnome-packagekit/icons/hicolor/*/*
%{_datadir}/gnome-packagekit/icons/hicolor/*/*/*.png
%{_datadir}/gnome-packagekit/icons/hicolor/scalable/*/*.svg*
%{_datadir}/icons/hicolor/*/*/*.png
%{_datadir}/icons/hicolor/scalable/*/*.svg*
%config(noreplace) %{_sysconfdir}/gconf/schemas/*.schemas
%{_datadir}/man/man1/*.1.gz
%{_datadir}/gnome/help/gnome-packagekit
%{python_sitelib}/packagekit/*py*
%{_datadir}/omf/gnome-packagekit
%{_sysconfdir}/xdg/autostart/gpk-update-icon.desktop
%{_datadir}/applications/gpk-application.desktop
%{_datadir}/applications/gpk-install-file.desktop
%{_datadir}/applications/gpk-prefs.desktop
%{_datadir}/applications/gpk-install-catalog.desktop
%{_datadir}/applications/gpk-log.desktop
%{_datadir}/applications/gpk-repo.desktop
%{_datadir}/applications/gpk-update-viewer.desktop

%files extra
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING NEWS README
%{_bindir}/gpk-backend-status
%{_bindir}/gpk-service-pack
%{_bindir}/gpk-update-viewer2
%{_datadir}/gnome-packagekit/gpk-service-pack.glade
%{_datadir}/gnome-packagekit/gpk-backend-status.glade
%{_datadir}/gnome-packagekit/gpk-update-viewer2.glade
%{_datadir}/applications/gpk-service-pack.desktop

%changelog
* Mon Mar 09 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.5-2
- Require PackageKit 0.4.5 otherwise the new update viewer breaks

* Mon Mar 09 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.5-1
- New upstream version
- Merge in a new update viewer with a very different UI which I've patched
  Fedora to use by default as requested by Matthias.
- Lots of translation updates

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 23 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.4-2
- Bump for rebuild.

* Mon Feb 23 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.4-1
- New upstream version
- Lots of bug fixes

* Mon Jan 19 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.2-1
- New upstream version
- Lots of bug fixes

* Thu Jan 08 2009 Richard Hughes  <rhughes@redhat.com> - 0.4.1-1
- New upstream version
- Add an option to the prefs dialog to prevent checking for updates when
  using mobile broadband connections
- Allow the admin to restrict getting updates when on WiFi connections
- Set the default search mode to details (not name) and preserve the search
  type in GConf if changed in the UI
- Add a simple markdown parser and use it in all applications.
- Send different errors when we fail a method on the session DBus interface
- Support setting timeouts via the interaction mode from the DBus interface
- Lots of bugfixes

* Fri Dec 12 2008 Richard Hughes  <rhughes@redhat.com> - 0.4.0-2
- Depend on PackageKit-gtk-module so the auto-font installation can be
  turned on in F11.
- Turn off the loading of libpk-gtk-module.so until we have a new
  fontconfig using a spec file patch that we can nuke soon.
- Fixes rh#476066

* Tue Dec 09 2008 Richard Hughes  <rhughes@redhat.com> - 0.4.0-1
- New upstream version

* Thu Dec  4 2008 Matthias Clasen <mclasen@redhat.com> 0.3.11-3
- Rebuild for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.3.11-2
- Rebuild for Python 2.6

* Mon Nov 24 2008 Richard Hughes <rhughes@redhat.com> - 0.3.11-1
- New upstream version

* Tue Nov 11 2008 Richard Hughes <rhughes@redhat.com> - 0.3.10-1
- New upstream version
- Drop all upstreamed patches

* Fri Nov 07 2008 Warren Togami <wtogami@redhat.com> - 0.3.9-7
- Bug #470617 Just exit instead of complaining about a non-local session

* Wed Nov 05 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-6
- Fix up the fedora system-install-packages compatibility script.
- Fixes #468568

* Sat Nov 01 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-5
- Fix up the pirut obsoletes to fix upgrades from F8. Fixes #469481

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-4
- Barr. Actually apply the patch. Sleep time.

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-3
- Fix the size request of gpk-application to fix rh#467987

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-2
- Split out the service pack creator and the backend status programs
  into a gnome-packagekit-extra package as it's not suitable for the
  default desktop.

* Mon Oct 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.9-1
- New upstream version
- Many new and updated translations.
- Lots of bugfixes (#467746, #467582)

* Fri Oct 24 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.8-2
- Fix the untitled window in gpk-update-viewer. Fixes #468200
- Fix the resize problem on small form factor devices. Fixes #467987

* Mon Oct 20 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.8-1
- New upstream version

* Mon Oct 13 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.7-1
- New upstream version
- Much better log viewer functionality
- New service pack creator tool

* Fri Oct 10 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-5
- Bump

* Fri Oct 10 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-4
- Add a bugfix from upstream so we don't try to check for updates
  when we've set to never. Fixes RH#461825.

* Wed Oct  8 2008 Matthias Clasen  <mclasen@redhat.com> - 0.3.6-3
- Another space-saving hack

* Mon Oct 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-2
- Upload new sources. Ooops.

* Mon Oct 06 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.6-1
- New upstream version
- Show vendor specific messages when we fail to find packages
- Turn off hardware HAL integration

* Mon Sep 22 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.5-1
- New upstream version

* Mon Sep 22 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.4-1
- New upstream version

* Wed Sep 17 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.3-2
- Fix the interaction when the update check and the upgrade check are
  scheduled at the same time.

* Tue Sep 16 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.3-1
- Update to newest upstream version.
- Supports collection install and remove in the UI
- Add InstallGStreamerCodecs to the session interface

* Mon Sep 08 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.2-1
- Update to newest upstream version.

* Thu Aug 28 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.1-3
- Bump because the PackageKit-devel rpm was empty.

* Thu Aug 28 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.1-2
- Bump as make chainbuild is broken, so we'll have to do this in two steps.

* Mon Aug 27 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.1-1
- Update to newest upstream version.

* Mon Aug 22 2008 Richard Hughes  <rhughes@redhat.com> - 0.3.0-1
- Update to newest upstream version.

* Mon Aug 04 2008 Robin Norwood <rnorwood@redhat.com> - 0.2.4-3
- Fix Source0 URL.

* Tue Jul 31 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.4-2
- Rebuild for libunique ABI break.

* Tue Jul 30 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.4-1
- New upstream version, only bugfixes.

* Wed Jun 18 2008 Richard Hughes  <rhughes@redhat.com> - 0.2.3-4.20080618
- Pull in a new snapshot from the unstable branch.
- Fixes a problem when installing with the DBUS session interface

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
