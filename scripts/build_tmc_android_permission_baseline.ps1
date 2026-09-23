$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$sdkRoot = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { 'E:\Android\Sdk' }
$buildTools = Join-Path $sdkRoot 'build-tools\34.0.0'
$androidJar = Join-Path $sdkRoot 'platforms\android-34\android.jar'
$appRoot = Join-Path $repoRoot 'benchmarks\android_permission_baseline_app'
$buildRoot = Join-Path $appRoot 'build'
$classes = Join-Path $buildRoot 'classes'
$dex = Join-Path $buildRoot 'dex'
$unsigned = Join-Path $buildRoot 'permission-baseline-unsigned.apk'
$aligned = Join-Path $buildRoot 'dros-tmc-permission-baseline.apk'
$keystore = Join-Path $buildRoot 'debug.keystore'
$source = Join-Path $appRoot 'src\io\dros\tmc\permissionbaseline\MainActivity.java'

New-Item -ItemType Directory -Force -Path $buildRoot, $classes, $dex | Out-Null
& (Join-Path $buildTools 'aapt2.exe') link -o $unsigned --manifest (Join-Path $appRoot 'AndroidManifest.xml') -I $androidJar
if ($LASTEXITCODE -ne 0) { throw 'aapt2 link failed' }
& javac -source 8 -target 8 -classpath $androidJar -d $classes $source
if ($LASTEXITCODE -ne 0) { throw 'javac failed' }
& (Join-Path $buildTools 'd8.bat') --lib $androidJar --output $dex (Join-Path $classes 'io\dros\tmc\permissionbaseline\MainActivity.class')
if ($LASTEXITCODE -ne 0) { throw 'd8 failed' }
& jar uf $unsigned -C $dex classes.dex
if ($LASTEXITCODE -ne 0) { throw 'jar update failed' }
& (Join-Path $buildTools 'zipalign.exe') -f 4 $unsigned $aligned
if ($LASTEXITCODE -ne 0) { throw 'zipalign failed' }
if (-not (Test-Path $keystore)) {
    & keytool -genkeypair -keystore $keystore -storepass android -alias androiddebugkey -keypass android -dname 'CN=Android Debug,O=Android,C=US' -keyalg RSA -keysize 2048 -validity 10000
}
& (Join-Path $buildTools 'apksigner.bat') sign --min-sdk-version 26 --ks $keystore --ks-pass pass:android --key-pass pass:android $aligned
if ($LASTEXITCODE -ne 0) { throw 'apksigner failed' }
Write-Output $aligned
