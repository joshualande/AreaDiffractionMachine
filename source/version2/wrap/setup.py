from distutils.core import setup,Extension

extension1 = Extension('MarCCDWrap', sources=['MarCCDWrap.c']) 
extension2 = Extension('DiffractionAnalysisWrap', sources=['DiffractionAnalysisWrap.c']) 
extension3 = Extension('UncompressWrap', sources=['UncompressWrap.c']) 
extension4 = Extension('DrawWrap', sources=['DrawWrap.c']) 
extension5 = Extension('PolygonWrap', sources=['PolygonWrap.c']) 
extension6 = Extension('FitWrap', sources=['FitWrap.c'],libraries=['levmar'],
       library_dirs=['levmar'],include_dirs=['levmar'] )

setup(name = "AllWrapedCode",
    version = "1.0",
    description = "Wraped code to do various useful things",
    maintainer = "Josh Lande",
    ext_modules = [ extension1,extension2,extension3,extension4,
            extension5,extension6 ]
)

