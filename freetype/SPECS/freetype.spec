%{!?with_xfree86:%define with_xfree86 1}

Summary: A free and portable font rendering engine
Name: freetype
Version: 2.9.1
Release: 10%{?dist}
License: (FTL or GPLv2+) and BSD and MIT and Public Domain and zlib with acknowledgement
Group: System Environment/Libraries
URL: http://www.freetype.org
Source:  http://download.savannah.gnu.org/releases/freetype/freetype-%{version}.tar.bz2
Source1: http://download.savannah.gnu.org/releases/freetype/freetype-doc-%{version}.tar.bz2
Source2: http://download.savannah.gnu.org/releases/freetype/ft2demos-%{version}.tar.bz2
Source3: ftconfig.h

Patch0:  freetype-2.3.0-enable-spr.patch

# Enable otvalid and gxvalid modules
Patch1:  freetype-2.2.1-enable-valid.patch
# Enable additional demos
Patch2:  freetype-2.5.2-more-demos.patch

Patch3:  freetype-2.6.5-libtool.patch

Patch4:  freetype-2.8-multilib.patch

Patch5:  freetype-2.9-ftsmooth.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1602501
Patch6:  freetype-2.9.1-covscan.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1890210
Patch7:  freetype-2.9.1-png-bitmap-size.patch
Patch8:  freetype-2.9.1-png-memory-leak.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=2077989
Patch9:  freetype-2.9.1-avoid-invalid-face-index.patch
Patch10: freetype-2.9.1-windres.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=2077991
Patch11:  freetype-2.9.1-properly-guard-face-index.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=2077985
Patch12:  freetype-2.9.1-guard-face-size.patch

# CVE-2025-27363
# https://access.redhat.com/security/cve/cve-2025-27363
# Patch by Marc Deslauriers of Canonical
Patch13: freetype-2.9.1-cve-2025-27363.patch

BuildRequires: libX11-devel
BuildRequires: libpng-devel
BuildRequires: zlib-devel
BuildRequires: bzip2-devel

Provides: %{name}-bytecode
Provides: %{name}-subpixel
Obsoletes: freetype-freeworld

%description
The FreeType engine is a free and portable font rendering
engine, developed to provide advanced font support for a variety of
platforms and environments. FreeType is a library which can open and
manages font files as well as efficiently load, hint and render
individual glyphs. FreeType is not a font server or a complete
text-rendering library.


%package demos
Summary: A collection of FreeType demos
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description demos
The FreeType engine is a free and portable font rendering
engine, developed to provide advanced font support for a variety of
platforms and environments.  The demos package includes a set of useful
small utilities showing various capabilities of the FreeType library.


%package devel
Summary: FreeType development libraries and header files
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: pkgconf%{?_isa}

%description devel
The freetype-devel package includes the static libraries and header files
for the FreeType font rendering engine.

Install freetype-devel if you want to develop programs which will use
FreeType.


%prep
%setup -q -b 1 -a 2

%patch0  -p1 -b .enable-spr
%patch1  -p1 -b .enable-valid

pushd ft2demos-%{version}
%patch2  -p1 -b .more-demos
popd

%patch3 -p1 -b .libtool
%patch4 -p1 -b .multilib
%patch5 -p1 -b .ftsmooth
%patch6 -p1 -b .covscan
%patch7 -p1 -b .png-bitmap-size
%patch8 -p1 -b .png-memory-leak
%patch9 -p1 -b .avoid-invalid-face-index
%patch10 -p1 -b .windres
%patch11 -p1 -b .properly-guard-face-index
%patch12 -p1 -b .guard-face-size
%patch13 -p1 -b .cve-2025-27363

%build

%configure --disable-static \
           --with-zlib=yes \
           --with-bzip2=yes \
           --with-png=yes \
           --enable-freetype-config \
           --with-harfbuzz=no
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' builds/unix/libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' builds/unix/libtool
make %{?_smp_mflags}

%if %{with_xfree86}
# Build demos
pushd ft2demos-%{version}
make TOP_DIR=".."
popd
%endif

# Convert FTL.txt and example3.cpp to UTF-8
pushd docs
iconv -f latin1 -t utf-8 < FTL.TXT > FTL.TXT.tmp && \
touch -r FTL.TXT FTL.TXT.tmp && \
mv FTL.TXT.tmp FTL.TXT

iconv -f iso-8859-1 -t utf-8 < "tutorial/example3.cpp" > "tutorial/example3.cpp.utf8"
touch -r tutorial/example3.cpp tutorial/example3.cpp.utf8 && \
mv tutorial/example3.cpp.utf8 tutorial/example3.cpp
popd


%install

%make_install gnulocaledir=$RPM_BUILD_ROOT%{_datadir}/locale

{
  for ftdemo in ftbench ftchkwd ftmemchk ftpatchk fttimer ftdump ftlint ftmemchk ftvalid ; do
      builds/unix/libtool --mode=install install -m 755 ft2demos-%{version}/bin/$ftdemo $RPM_BUILD_ROOT/%{_bindir}
  done
}
%if %{with_xfree86}
{
  for ftdemo in ftdiff ftgamma ftgrid ftmulti ftstring fttimer ftview ; do
      builds/unix/libtool --mode=install install -m 755 ft2demos-%{version}/bin/$ftdemo $RPM_BUILD_ROOT/%{_bindir}
  done
}
%endif

# fix multilib issues
%define wordsize %{__isa_bits}

mv $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig.h \
   $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig-%{wordsize}.h
install -p -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_includedir}/freetype2/freetype/config/ftconfig.h

# Don't package static .a or .la files
rm -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}


%triggerpostun -- freetype < 2.0.5-3
{
  # ttmkfdir updated - as of 2.0.5-3, on upgrades we need xfs to regenerate
  # things to get the iso10646-1 encoding listed.
  for I in %{_datadir}/fonts/*/TrueType /usr/share/X11/fonts/TTF; do
      [ -d $I ] && [ -f $I/fonts.scale ] && [ -f $I/fonts.dir ] && touch $I/fonts.scale
  done
  exit 0
}

%ldconfig_scriptlets

%files
%{!?_licensedir:%global license %%doc}
%license docs/LICENSE.TXT docs/FTL.TXT docs/GPLv2.TXT
%{_libdir}/libfreetype.so.*
%doc README

%files demos
%{_bindir}/ftbench
%{_bindir}/ftchkwd
%{_bindir}/ftmemchk
%{_bindir}/ftpatchk
%{_bindir}/fttimer
%{_bindir}/ftdump
%{_bindir}/ftlint
%{_bindir}/ftvalid
%if %{with_xfree86}
%{_bindir}/ftdiff
%{_bindir}/ftgamma
%{_bindir}/ftgrid
%{_bindir}/ftmulti
%{_bindir}/ftstring
%{_bindir}/ftview
%endif
%doc ChangeLog README

%files devel
%doc docs/CHANGES docs/formats.txt docs/ft2faq.html
%dir %{_includedir}/freetype2
%{_datadir}/aclocal/freetype2.m4
%{_includedir}/freetype2/*
%{_libdir}/libfreetype.so
%{_bindir}/freetype-config
%{_libdir}/pkgconfig/freetype2.pc
%doc docs/design
%doc docs/glyphs
%doc docs/reference
%doc docs/tutorial
%{_mandir}/man1/*

%changelog
* Fri Mar 14 2025 Jonathan Wright <jonathan@almalinux.org> - 2.9.1-10
- Fix CVE-2025-27363 Out-of-bounds Write
- Resolves: RHEL-83094

* Fri May 27 2022 Marek Kasik <mkasik@redhat.com> - 2.9.1-9
- Guard face->size
- Resolves: #2079279

* Thu May 26 2022 Marek Kasik <mkasik@redhat.com> - 2.9.1-8
- Properly guard "face_index"
- Resolves: #2079261

* Thu May 26 2022 Marek Kasik <mkasik@redhat.com> - 2.9.1-7
- Do not search for windres
- Resolves: #2079270

* Wed May 25 2022 Marek Kasik <mkasik@redhat.com> - 2.9.1-6
- Avoid invalid face index
- Resolves: #2079270

* Thu Nov  5 2020 Marek Kasik <mkasik@redhat.com> - 2.9.1-5
- Test bitmap size earlier for PNGs
- Fix memory leak in pngshim.c
- Resolves: #1891906

* Fri Dec  7 2018 Marek Kasik <mkasik@redhat.com> - 2.9.1-4
- Use pkgconf in freetype-config.in directly (RPMDiff)
- Related: #1651252

* Fri Dec  7 2018 Marek Kasik <mkasik@redhat.com> - 2.9.1-3
- Enable ClearType subpixel rendering
- Resolves: #1651252

* Thu Sep  6 2018 Marek Kasik <mkasik@redhat.com> - 2.9.1-2
- Fix important issues found by covscan
- Resolves: #1602501

* Wed Jun 27 2018 Marek Kasik <mkasik@redhat.com> - 2.9.1-1
- Update to 2.9.1
- Modify/remove/add patches as needed
- Resolves: #1595787

* Fri Feb 16 2018 Marek Kasik <mkasik@redhat.com> - 2.8-10
- Avoid NULL reference
- Resolves: #1544776

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.8-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Feb 02 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 2.8-8
- Switch to %%ldconfig_scriptlets

* Mon Oct  9 2017 Marek Kasik <mkasik@redhat.com> - 2.8-7
- Require pkgconf so we can make freetype-config multilib compatible again
- Resolves: #1497443

* Thu Sep 21 2017 Marek Kasik <mkasik@redhat.com> - 2.8-6
- Fix loading of named instances (TrueType)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.8-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun  1 2017 Marek Kasik <mkasik@redhat.com> - 2.8-3
- Adjust loop counter maximum for TrueType fonts
- Resolves: #1456585

* Wed May 24 2017 Marek Kasik <mkasik@redhat.com> - 2.8-2
- Accept ISO646.1991-IRV as a Unicode charmap in PCF and BDF drivers
- Resolves: #1451795

* Wed May 17 2017 Marek Kasik <mkasik@redhat.com> - 2.8-1
- Update to 2.8
- Modify/remove patches as needed
- Resolves: #1450581

* Tue May  2 2017 Marek Kasik <mkasik@redhat.com> - 2.7.1-7
- Fix numbers of tracking bugs

* Tue May  2 2017 Marek Kasik <mkasik@redhat.com> - 2.7.1-6
- Add safety guard (CVE-2017-8287)
- Resolves: #1446074

* Tue May  2 2017 Marek Kasik <mkasik@redhat.com> - 2.7.1-5
- Better protect `flex' handling (CVE-2017-8105)
- Resolves: #1446501

* Mon Apr 10 2017 Marek Kasik <mkasik@redhat.com> - 2.7.1-4
- Revert previous commit
- Related: #1437999

* Mon Apr  3 2017 Marek Kasik <mkasik@redhat.com> - 2.7.1-3
- Allow linear scaling for unhinted rendering
- Resolves: #1437999

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan  3 2017 Marek Kasik <mkasik@redhat.com> - 2.7.1-1
- Update to 2.7.1
- Resolves: #1409271

* Mon Nov 21 2016 Marek Kasik <mkasik@redhat.com> - 2.7-2
- Fix a valgrind warning
- Resolves: #1395915

* Mon Sep 12 2016 Marek Kasik <mkasik@redhat.com> - 2.7-1
- Update to 2.7
- Resolves: #1374305

* Mon Aug 22 2016 Marek Kasik <mkasik@redhat.com> - 2.6.5-2
- Don't show path of non-existing libtool file

* Wed Jul 13 2016 Marek Kasik <mkasik@redhat.com> - 2.6.5-1
- Update to 2.6.5
- Resolves: #1355743

* Sat Mar  5 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2.6.3-2
- Use %%license and cleanup spec
- Move dev docs to devel package

* Wed Feb 10 2016 Marek Kasik <mkasik@redhat.com> - 2.6.3-1
- Update to 2.6.3

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Dec  3 2015 Tom Callaway <spot@fedoraproject.org> - 2.6.2-1
- update to 2.6.2

* Mon Oct 12 2015 Marek Kasik <mkasik@redhat.com> - 2.6.1-1
- Update to 2.6.1
- Adapt to the new header structure
- Resolves: #1268661

* Tue Jul 28 2015 Marek Kasik <mkasik@redhat.com> - 2.6.0-3
- Don't use `hmtx' table for LSB

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Marek Kasik <mkasik@redhat.com> - 2.6.0-1
- Update to 2.6
- Resolves: #1229688

* Tue Jan  6 2015 Marek Kasik <mkasik@redhat.com> - 2.5.5-1
- Update to 2.5.5
- Resolves: #1178876

* Tue Dec  9 2014 Marek Kasik <mkasik@redhat.com> - 2.5.4-1
- Update to 2.5.4
- Resolves: #1171504

* Tue Nov 11 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-11
- Fix directories returned by freetype-config with modified prefix
- Resolves: #1161963

* Tue Oct 21 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-10
- Fix patch which enables subpixel rendering
- Resolves: #1154448

* Mon Aug 18 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-9
- Simplify getting of wordsize

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Aug  2 2014 Peter Robinson <pbrobinson@redhat.com> 2.5.3-7
- Generic 32/64 bit platform detection (fix it once and for all)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 25 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-5
- Be explicit about required libraries

* Tue Mar 25 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-4
- Don't return flags of privately used libraries when
- calling "freetype-config --libs"
- Resolves: #1079302

* Fri Mar 21 2014 Dan Horák <dan[at]danny.cz> - 2.5.3-3
- drop private libs from freetype-config so it returns the same libs as pkg-config

* Tue Mar 11 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-2
- Enable support for bzip2 compressed fonts

* Tue Mar 11 2014 Marek Kasik <mkasik@redhat.com> - 2.5.3-1
- Update to 2.5.3
- Resolves: #1073923

* Mon Jan 20 2014 Marek Kasik <mkasik@redhat.com> - 2.5.2-2
- Fix include directory in freetype-config
- Resolves: #1055154

* Fri Jan 17 2014 Marek Kasik <mkasik@redhat.com> - 2.5.2-1
- Update to 2.5.2
- Modify spec file to respect the new header file layout
- Resolves: #1034065

* Fri Jan 10 2014 Marek Kasik <mkasik@redhat.com> - 2.5.0-5
- Enable ppc64le architecture
- Resolves: #1051202

* Fri Sep 20 2013 Marek Kasik <mkasik@redhat.com> - 2.5.0-4
- Fix vertical size of emboldened glyphs

* Mon Aug 05 2013 Marek Kasik <mkasik@redhat.com> - 2.5.0-3
- Fix changelog dates

* Mon Aug 05 2013 Marek Kasik <mkasik@redhat.com> - 2.5.0-2
- Require libpng

* Mon Aug 05 2013 Marek Kasik <mkasik@redhat.com> - 2.5.0-1
- Update to 2.5.0
- Backport changes from freetype-2.5.0.1
-   (ft2demos-2.5.0.1 and freetype-doc-2.5.0.1 were not released)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed May 29 2013 Peter Robinson <pbrobinson@fedoraproject.org> 2.4.12-5
- Add aarch64 to 64 bit arch list

* Thu May 16 2013 Marek Kasik <mkasik@redhat.com> - 2.4.12-4
- Change encoding of "docs/tutorial/example3.cpp" to UTF-8

* Thu May 16 2013 Marek Kasik <mkasik@redhat.com> - 2.4.12-3
- Package ftconfig.h as source file

* Mon May 13 2013 Marek Kasik <mkasik@redhat.com> - 2.4.12-2
- Don't use quotes in freetype2.pc
- Resolves: #961855

* Thu May  9 2013 Marek Kasik <mkasik@redhat.com> - 2.4.12-1
- Update to 2.4.12
- Enable Adobe CFF engine
- Resolves: #959771

* Tue Mar 19 2013 Marek Kasik <mkasik@redhat.com> - 2.4.11-3
- Fix emboldening:
    - split out MSB function
    - fix integer overflows
    - fix broken emboldening at small sizes
- Resolves: #891457

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan  2 2013 Marek Kasik <mkasik@redhat.com> - 2.4.11-1
- Update to 2.4.11
- Resolves: #889177

* Wed Oct 24 2012 Marek Kasik <mkasik@redhat.com> - 2.4.10-3
- Update License field

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Marek Kasik <mkasik@redhat.com> 2.4.10-1
- Update to 2.4.10
- Remove patches which are already included in upstream
- Resolves: #832651

* Fri Mar 30 2012 Marek Kasik <mkasik@redhat.com> 2.4.9-1
- Update to 2.4.9
- Fixes various CVEs
- Resolves: #806270

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 15 2011 Marek Kasik <mkasik@redhat.com> 2.4.8-1
- Update to 2.4.8
- Remove an unneeded patch

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.7-2
- Rebuilt for glibc bug#747377

* Thu Oct 20 2011 Marek Kasik <mkasik@redhat.com> 2.4.7-1
- Update to 2.4.7
- Fixes CVE-2011-3256
- Resolves: #747262

* Thu Aug  4 2011 Marek Kasik <mkasik@redhat.com> 2.4.6-1
- Update to 2.4.6

* Wed Jul 20 2011 Marek Kasik <mkasik@redhat.com> 2.4.5-2
- Add freetype-2.4.5-CVE-2011-0226.patch
    (Add better argument check for `callothersubr'.)
    - based on patches by Werner Lemberg,
      Alexei Podtelezhnikov and Matthias Drochner
- Resolves: #723469

* Tue Jun 28 2011 Marek Kasik <mkasik@redhat.com> 2.4.5-1
- Update to 2.4.5

* Tue Mar  8 2011 Marek Kasik <mkasik@redhat.com> 2.4.4-4
- Fix autohinting fallback (#547532).
- Ignore CFF-based OTFs.

* Sun Feb 20 2011 Marek Kasik <mkasik@redhat.com> 2.4.4-3
- Enable bytecode interpreter (#547532).
- Fall back to autohinting if a TTF/OTF doesn't contain any bytecode.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec  2 2010 Marek Kasik <mkasik@redhat.com> 2.4.4-1
- Update to 2.4.4
- Remove freetype-2.4.3-CVE-2010-3855.patch
- Resolves: #659020

* Mon Nov 15 2010 Marek Kasik <mkasik@redhat.com> 2.4.3-2
- Add freetype-2.4.3-CVE-2010-3855.patch
    (Protect against invalid `runcnt' values.)
- Resolves: #651764

* Tue Oct 26 2010 Marek Kasik <mkasik@redhat.com> 2.4.3-1
- Update to 2.4.3
- Resolves: #639906

* Wed Oct  6 2010 Marek Kasik <mkasik@redhat.com> 2.4.2-3
- Add freetype-2.4.2-CVE-2010-3311.patch
    (Don't seek behind end of stream.)
- Resolves: #638522

* Fri Aug  6 2010 Matthias Clasen <mclasen@redhat.com> 2.4.2-2
- Fix a thinko, we still want to disable the bytecode interpreter
  by default

* Fri Aug  6 2010 Matthias Clasen <mclasen@redhat.com> 2.4.2-1
- Update to 2.4.2
- Drop upstreamed patch, bytecode interpreter now on by default

* Tue Feb 23 2010 Behdad Esfahbod <behdad@redhat.com> 2.3.12-1
- Update to 2.3.12
- Drop mathlib patch

* Thu Dec  3 2009 Behdad Esfahbod <behdad@redhat.com> 2.3.11-2
- Drop upstreamed patch.
- Enable patented bytecode interpretter now that the patents are expired.

* Thu Oct 22 2009 Behdad Esfahbod <behdad@redhat.com> 2.3.11-1
- Update to 2.3.11.
- Add freetype-2.3.11-more-demos.patch
- New demo programs ftmemchk, ftpatchk, and fttimer

* Thu Oct 08 2009 Behdad Esfahbod <behdad@redhat.com> 2.3.10-1
- Drop freetype-2.3.9-aliasing.patch
- Update to 2.3.10.

* Thu Jul 30 2009 Behdad Esfahbod <behdad@redhat.com> 2.3.9-6
- Add freetype-2.3.9-aliasing.patch
- Resolves: 513582

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.9-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu May  7 2009 Matthias Clasen <mclasen@redhat.com> 2.3.9-4
- Don't own /usr/lib/pkgconfig

* Fri Mar 27 2009 Behdad Esfahbod <besfahbo@redhat.com> 2.3.9-3
- Disable subpixel hinting by default.  Was turned on unintentionally.

* Wed Mar 25 2009 Behdad Esfahbod <besfahbo@redhat.com> 2.3.9-2
- Add Provides: freetype-bytecode and freetype-subpixel if built
  with those options.
- Resolves: #155210

* Fri Mar 13 2009 Behdad Esfahbod <besfahbo@redhat.com> 2.3.9-1
- Update to 2.3.9.
- Resolves #489928

* Mon Mar 09 2009 Behdad Esfahbod <besfahbo@redhat.com> 2.3.8-2.1
- Preserve timestamp of FTL.TXT when converting to UTF-8.

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Behdad Esfahbod <besfahbo@redhat.com> 2.3.8-1
- Update to 2.3.8
- Remove freetype-autohinter-ligature.patch

* Tue Dec 09 2008 Behdad Esfahbod <besfahbo@redhat.com> 2.3.7-3
- Add full source URL to Source lines.
- Add docs to main and devel package.
- rpmlint is happy now.
- Resolves: #225770

* Fri Dec 05 2008 Behdad Esfahbod <besfahbo@redhat.com> 2.3.7-2
- Add freetype-autohinter-ligature.patch
- Resolves: #368561

* Thu Aug 14 2008 Behdad Esfahbod <besfahbo@redhat.com> 2.3.7-1
- Update to 2.3.7

* Tue Jun 10 2008 Behdad Esfahbod <besfahbo@redhat.com> 2.3.6-1
- Update to 2.3.6

* Wed May 21 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.3.5-5
- fix license tag
- add sparc64 to list of 64bit arches

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.3.5-4
- Autorebuild for GCC 4.3

* Thu Aug 23 2007 Adam Jackson <ajax@redhat.com> - 2.3.5-3
- Rebuild for build ID

* Tue Jul 31 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.5-2
- Change spec file to permit enabling bytecode-interpreter and
  subpixel-rendering without editing spec file.
- Resolves: 249986

* Wed Jul 25 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.5-1
- Update to 2.3.5.
- Drop freetype-2.3.4-ttf-overflow.patch

* Fri Jun 29 2007 Adam Jackson <ajax@redhat.com> 2.3.4-4
- Fix builds/unix/libtool to not emit rpath into binaries. (#225770)

* Thu May 31 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.4-3
- Add freetype-2.3.4-ttf-overflow.patch

* Thu Apr 12 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.4-2
- Add alpha to 64-bit archs (#236166)

* Thu Apr 05 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.4-1
- Update to 2.3.4.

* Thu Apr 05 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.3-2
- Include new demos ftgrid and ftdiff in freetype-demos. (#235478)

* Thu Apr 05 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.3-1
- Update to 2.3.3.

* Fri Mar 09 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.2-1
- Update to 2.3.2.

* Fri Feb 02 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.1-1
- Update to 2.3.1.

* Wed Jan 17 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.0-2
- Add without_subpixel_rendering.
- Drop X11_PATH=/usr.  Not needed anymore.

* Wed Jan 17 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.3.0-1
- Update to 2.3.0.
- Drop upstream patches.
- Drop -fno-strict-aliasing, it should just work.
- Fix typo in ftconfig.h generation.

* Tue Jan 09 2007 Behdad Esfahbod <besfahbo@redhat.com> 2.2.1-16
- Backport binary-search fixes from HEAD
- Add freetype-2.2.1-ttcmap.patch
- Resolves: #208734

- Fix rendering issue with some Asian fonts.
- Add freetype-2.2.1-fix-get-orientation.patch
- Resolves: #207261

- Copy non-X demos even if not compiling with_xfree86.

- Add freetype-2.2.1-zero-item-size.patch, to fix crasher.
- Resolves #214048

- Add X11_PATH=/usr to "make"s, to find modern X.
- Resolves #212199

* Mon Sep 11 2006 Behdad Esfahbod <besfahbo@redhat.com> 2.2.1-10
- Fix crasher https://bugs.freedesktop.org/show_bug.cgi?id=6841
- Add freetype-2.2.1-memcpy-fix.patch

* Thu Sep 07 2006 Behdad Esfahbod <besfahbo@redhat.com> 2.2.1-9
- Add BuildRequires: libX11-devel (#205355)

* Tue Aug 29 2006 Behdad Esfahbod <besfahbo@redhat.com> 2.2.1-8
- Add freetype-composite.patch and freetype-more-composite.patch
  from upstream. (#131851)

* Mon Aug 28 2006 Matthias Clasen <mclasen@redhat.com> - 2.2.1-7
- Require pkgconfig in the -devel package

* Fri Aug 18 2006 Jesse Keating <jkeating@redhat.com> - 2.2.1-6
- pass --disable-static to %%configure. (#172628)

* Thu Aug 17 2006 Jesse Keating <jkeating@redhat.com> - 2.2.1-5
- don't package static libs

* Sun Aug 13 2006 Matthias Clasen <mclasen@redhat.com> - 2.2.1-4.fc6
- fix a problem with the multilib patch (#202366)

* Thu Jul 27 2006 Matthias Clasen  <mclasen@redhat.com> - 2.2.1-3
- fix multilib issues

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.2.1-2.1
- rebuild

* Fri Jul 07 2006 Behdad Esfahbod <besfahbo@redhat.com> 2.2.1-2
- Remove unused BuildRequires

* Fri Jul 07 2006 Behdad Esfahbod <besfahbo@redhat.com> 2.2.1-1
- Update to 2.2.1
- Remove FreeType 1, to move to extras
- Install new demos ftbench, ftchkwd, ftgamma, and ftvalid
- Enable modules gxvalid and otvalid

* Wed May 17 2006 Karsten Hopp <karsten@redhat.de> 2.1.10-6
- add buildrequires libICE-devel, libSM-devel

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.1.10-5.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.1.10-5.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 18 2005 Bill Nottingham  <notting@redhat.com> 2.1.10-5
- Remove references to obsolete /usr/X11R6 paths

* Tue Nov  1 2005 Matthias Clasen  <mclasen@redhat.com> 2.1.10-4
- Switch requires to modular X

* Fri Oct 21 2005 Matthias Clasen  <mclasen@redhat.com> 2.1.10-3
- BuildRequire gettext 

* Wed Oct 12 2005 Jason Vas Dias <jvdias@redhat.com> 2.1.10-2
- fix 'without_bytecode_interpreter 0' build: freetype-2.1.10-enable-ft2-bci.patch

* Fri Oct  7 2005 Matthias Clasen  <mclasen@redhat.com> 2.1.10-1
- Update to 2.1.10
- Add necessary fixes

* Tue Aug 16 2005 Kristian Høgsberg <krh@redhat.com> 2.1.9-4
- Fix freetype-config on 64 bit platforms.

* Thu Jul 07 2005 Karsten Hopp <karsten@redhat.de> 2.1.9-3
- BuildRequires xorg-x11-devel

* Fri Mar  4 2005 David Zeuthen <davidz@redhat.com> - 2.1.9-2
- Rebuild

* Wed Aug  4 2004 Owen Taylor <otaylor@redhat.com> - 2.1.9-1
- Upgrade to 2.1.9
- Since we are just using automake for aclocal, use it unversioned,
  instead of specifying 1.4.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon Apr 19 2004 Owen Taylor <otaylor@redhat.com> 2.1.7-4
- Add patch from freetype CVS to fix problem with eexec (#117743)
- Add freetype-devel to buildrequires and -devel requires
  (Maxim Dzumanenko, #111108)

* Wed Mar 10 2004 Mike A. Harris <mharris@redhat.com> 2.1.7-3
- Added -fno-strict-aliasing to CFLAGS and CXXFLAGS to try to fix SEGV and
  SIGILL crashes in mkfontscale which have been traced into freetype and seem
  to be caused by aliasing issues in freetype macros (#118021)

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com> 2.1.7-2.1
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com> 2.1.7-2
- rebuilt

* Fri Jan 23 2004 Owen Taylor <otaylor@redhat.com> 2.1.7-1
- Upgrade to 2.1.7

* Tue Sep 23 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- allow compiling without the demos as that requires XFree86
  (this allows bootstrapping XFree86 on new archs)

* Fri Aug  8 2003 Elliot Lee <sopwith@redhat.com> 2.1.4-4.1
- Rebuilt

* Tue Jul  8 2003 Owen Taylor <otaylor@redhat.com> 2.1.4-4.0
- Bump for rebuild

* Wed Jun 25 2003 Owen Taylor <otaylor@redhat.com> 2.1.4-3
- Fix crash with non-format-0 hdmx tables (found by David Woodhouse)

* Mon Jun  9 2003 Owen Taylor <otaylor@redhat.com> 2.1.4-1
- Version 2.1.4
- Relibtoolize to get deplibs right for x86_64
- Use autoconf-2.5x for freetype-1.4 to fix libtool-1.5 compat problem (#91781)
- Relativize absolute symlinks to fix the -debuginfo package 
  (#83521, Mike Harris)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu May 22 2003 Jeremy Katz <katzj@redhat.com> 2.1.3-9
- fix build with gcc 3.3

* Tue Feb 25 2003 Owen Taylor <otaylor@redhat.com>
- Add a memleak fix for the gzip backend from Federic Crozat

* Thu Feb 13 2003 Elliot Lee <sopwith@redhat.com> 2.1.3-7
- Run libtoolize/aclocal/autoconf so that libtool knows to generate shared libraries 
  on ppc64.
- Use _smp_mflags (for freetype 2.x only)

* Tue Feb  4 2003 Owen Taylor <otaylor@redhat.com>
- Switch to using %%configure (should fix #82330)

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Mon Jan  6 2003 Owen Taylor <otaylor@redhat.com> 2.1.3-4
- Make FreeType robust against corrupt fonts with recursive composite 
  glyphs (#74782, James Antill)

* Thu Jan  2 2003 Owen Taylor <otaylor@redhat.com> 2.1.3-3
- Add a patch to implement FT_LOAD_TARGET_LIGHT
- Fix up freetype-1.4-libtool.patch 

* Thu Dec 12 2002 Mike A. Harris <mharris@redhat.com> 2.1.3-2
- Update to freetype 2.1.3
- Removed ttmkfdir sources and patches, as they have been moved from the
  freetype packaging to XFree86 packaging, and now to the ttmkfdir package
- Removed patches that are now included in 2.1.3:
  freetype-2.1.1-primaryhints.patch, freetype-2.1.2-slighthint.patch,
  freetype-2.1.2-bluefuzz.patch, freetype-2.1.2-stdw.patch,
  freetype-2.1.2-transform.patch, freetype-2.1.2-autohint.patch,
  freetype-2.1.2-leftright.patch
- Conditionalized inclusion of freetype 1.4 library.

* Wed Dec 04 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- disable perl, it is not used at all

* Tue Dec 03 2002 Elliot Lee <sopwith@redhat.com> 2.1.2-11
- Instead of removing unpackaged file, include it in the package.

* Sat Nov 30 2002 Mike A. Harris <mharris@redhat.com> 2.1.2-10
- Attempted to fix lib64 issue in freetype-demos build with X11_LINKLIBS
- Cleaned up various _foodir macros throughtout specfile
- Removed with_ttmkfdir build option as it is way obsolete

* Fri Nov 29 2002 Tim Powers <timp@redhat.com> 2.1.2-8
- remove unpackaged files from the buildroot

* Wed Aug 28 2002 Owen Taylor <otaylor@redhat.com>
- Fix a bug with PCF metrics

* Fri Aug  9 2002 Owen Taylor <otaylor@redhat.com>
- Backport autohinter improvements from CVS

* Tue Jul 23 2002 Owen Taylor <otaylor@redhat.com>
- Fix from CVS for transformations (#68964)

* Tue Jul  9 2002 Owen Taylor <otaylor@redhat.com>
- Add another bugfix for the postscript hinter

* Mon Jul  8 2002 Owen Taylor <otaylor@redhat.com>
- Add support for BlueFuzz private dict value, fixing rendering 
  glitch for Luxi Mono.

* Wed Jul  3 2002 Owen Taylor <otaylor@redhat.com>
- Add an experimental FT_Set_Hint_Flags() call

* Mon Jul  1 2002 Owen Taylor <otaylor@redhat.com>
- Update to 2.1.2
- Add a patch fixing freetype PS hinter bug

* Fri Jun 21 2002 Mike A. Harris <mharris@redhat.com> 2.1.1-2
- Added ft rpm build time conditionalizations upon user requests

* Tue Jun 11 2002 Owen Taylor <otaylor@redhat.com> 2.1.1-1
- Version 2.1.1

* Mon Jun 10 2002 Owen Taylor <otaylor@redhat.com>
- Add a fix for PCF character maps

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri May 17 2002 Mike A. Harris <mharris@redhat.com> 2.1.0-2
- Updated freetype to version 2.1.0
- Added libtool fix for freetype 1.4 (#64631)

* Wed Mar 27 2002 Nalin Dahyabhai <nalin@redhat.com> 2.0.9-2
- use "libtool install" instead of "install" to install some binaries (#62005)

* Mon Mar 11 2002 Mike A. Harris <mharris@redhat.com> 2.0.9-1
- Updated to freetype 2.0.9

* Sun Feb 24 2002 Mike A. Harris <mharris@redhat.com> 2.0.8-4
- Added proper docs+demos source for 2.0.8.

* Sat Feb 23 2002 Mike A. Harris <mharris@redhat.com> 2.0.8-3
- Added compat patch so 2.x works more like 1.x
- Rebuilt with new build toolchain

* Fri Feb 22 2002 Mike A. Harris <mharris@redhat.com> 2.0.8-2
- Updated to freetype 2.0.8, however docs and demos are stuck at 2.0.7
  on the freetype website.  Munged specfile to deal with the problem by using
  {oldversion} instead of version where appropriate.  <sigh>

* Sat Feb  2 2002 Tim Powers <timp@redhat.com> 2.0.6-3
- bumping release so that we don't collide with another build of
  freetype, make sure to change the release requirement in the XFree86
  package

* Fri Feb  1 2002 Mike A. Harris <mharris@redhat.com> 2.0.6-2
- Made ttmkfdir inclusion conditional, and set up a define to include
  ttmkfdir in RHL 7.x builds, since ttmkfdir is now moving to the new
  XFree86-font-utils package.

* Wed Jan 16 2002 Mike A. Harris <mharris@redhat.com> 2.0.6-1
- Updated freetype to version 2.0.6

* Wed Jan 09 2002 Tim Powers <timp@redhat.com> 2.0.5-4
- automated rebuild

* Fri Nov 30 2001 Elliot Lee <sopwith@redhat.com> 2.0.5-3
- Fix bug #56901 (ttmkfdir needed to list Unicode encoding when generating
  font list). (ttmkfdir-iso10646.patch)
- Use _smp_mflags macro everywhere relevant. (freetype-pre1.4-make.patch)
- Undo fix for #24253, assume compiler was fixed.

* Mon Nov 12 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.0.5-2
- Fix build with gcc 3.1 (#56079)

* Sun Nov 11 2001 Mike A. Harris <mharris@redhat.com> 2.0.5-1
- Updated freetype to version 2.0.5

* Sat Sep 22 2001 Mike A. Harris <mharris@redhat.com> 2.0.4-2
- Added new subpackage freetype-demos, added demos to build
- Disabled ftdump, ftlint in utils package favoring the newer utils in
  demos package.

* Tue Sep 11 2001 Mike A. Harris <mharris@redhat.com> 2.0.4-1
- Updated source to 2.0.4
- Added freetype demo's back into src.rpm, but not building yet.

* Wed Aug 15 2001 Mike A. Harris <mharris@redhat.com> 2.0.3-7
- Changed package to use {findlang} macro to fix bug (#50676)

* Sun Jul 15 2001 Mike A. Harris <mharris@redhat.com> 2.0.3-6
- Changed freetype-devel to group Development/Libraries (#47625)

* Mon Jul  9 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.0.3-5
- Fix up FT1 headers to please Qt 3.0.0 beta 2

* Sun Jun 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.0.3-4
- Add ft2build.h to -devel package, since it's included by all other
  freetype headers, the package is useless without it

* Thu Jun 21 2001 Nalin Dahyabhai <nalin@redhat.com> 2.0.3-3
- Change "Requires: freetype = name/ver" to "freetype = version/release",
  and move the requirements to the subpackages.

* Mon Jun 18 2001 Mike A. Harris <mharris@redhat.com> 2.0.3-2
- Added "Requires: freetype = name/ver"

* Tue Jun 12 2001 Mike A. Harris <mharris@redhat.com> 2.0.3-1
- Updated to Freetype 2.0.3, minor specfile tweaks.
- Freetype2 docs are is in a separate tarball now. Integrated it.
- Built in new environment.

* Fri Apr 27 2001 Bill Nottingham <notting@redhat.com>
- rebuild for C++ exception handling on ia64

* Sat Jan 20 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Build ttmkfdir with -O0, workaround for Bug #24253

* Fri Jan 19 2001 Nalin Dahyabhai <nalin@redhat.com>
- libtool is used to build libttf, so use libtool to link ttmkfdir with it
- fixup a paths for a couple of missing docs

* Thu Jan 11 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Update ttmkfdir

* Wed Dec 27 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Update to 2.0.1 and 1.4
- Mark locale files as such

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jun 12 2000 Preston Brown <pbrown@redhat.com>
- move .la file to devel pkg
- FHS paths

* Thu Feb 17 2000 Preston Brown <pbrown@redhat.com>
- revert spaces patch, fix up some foundry names to match X ones

* Mon Feb 07 2000 Nalin Dahyabhai <nalin@redhat.com>
- add defattr, ftmetric, ftsbit, ftstrtto per bug #9174

* Wed Feb 02 2000 Cristian Gafton <gafton@redhat.com>
- fix description and summary

* Wed Jan 12 2000 Preston Brown <pbrown@redhat.com>
- make ttmkfdir replace spaces in family names with underscores (#7613)

* Tue Jan 11 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 1.3.1
- handle RPM_OPT_FLAGS

* Wed Nov 10 1999 Preston Brown <pbrown@redhat.com>
- fix a path for ttmkfdir Makefile

* Thu Aug 19 1999 Preston Brown <pbrown@redhat.com>
- newer ttmkfdir that works better, moved ttmkfdir to /usr/bin from /usr/sbin
- freetype utilities moved to subpkg, X dependency removed from main pkg
- libttf.so symlink moved to devel pkg

* Mon Mar 22 1999 Preston Brown <pbrown@redhat.com>
- strip binaries

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 5)

* Thu Mar 18 1999 Cristian Gafton <gafton@redhat.com>
- fixed the doc file list

* Wed Feb 24 1999 Preston Brown <pbrown@redhat.com>
- Injected new description and group.

* Mon Feb 15 1999 Preston Brown <pbrown@redhat.com>
- added ttmkfdir

* Tue Feb 02 1999 Preston Brown <pbrown@redhat.com>
- update to 1.2

* Thu Jan 07 1999 Cristian Gafton <gafton@redhat.com>
- call libtoolize to sanitize config.sub and get ARM support
- dispoze of the patch (not necessary anymore)

* Wed Oct 21 1998 Preston Brown <pbrown@redhat.com>
- post/postun sections for ldconfig action.

* Tue Oct 20 1998 Preston Brown <pbrown@redhat.com>
- initial RPM, includes normal and development packages.
