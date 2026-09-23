$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$sdkRoot = if ($env:ANDROID_HOME) { $env:ANDROID_HOME } else { 'E:\Android\Sdk' }
$buildTools = Join-Path $sdkRoot 'build-tools\34.0.0'
$androidJar = Join-Path $sdkRoot 'platforms\android-34\android.jar'
$keystoreRoot = Join-Path $repoRoot 'benchmarks\android_binder_baseline_build'
$keystore = Join-Path $keystoreRoot 'debug.keystore'

function Build-BinderApk {
    param(
        [string]$AppName,
        [string]$PackagePath,
        [string]$ManifestPath,
        [string]$ClassPath,
        [string]$OutputName
    )

    $appRoot = Join-Path $repoRoot $PackagePath
    $buildRoot = Join-Path $appRoot 'build'
    $classes = Join-Path $buildRoot 'classes'
    $dex = Join-Path $buildRoot 'dex'
    $unsigned = Join-Path $buildRoot "$AppName-unsigned.apk"
    $aligned = Join-Path $buildRoot $OutputName
    $source = Join-Path $appRoot $ClassPath

    New-Item -ItemType Directory -Force -Path $buildRoot, $classes, $dex, $keystoreRoot | Out-Null
    Remove-Item -Force -ErrorAction SilentlyContinue $unsigned, $aligned

    & (Join-Path $buildTools 'aapt2.exe') link -o $unsigned --manifest (Join-Path $appRoot $ManifestPath) -I $androidJar
    if ($LASTEXITCODE -ne 0) { throw "$AppName aapt2 link failed" }
    & javac -source 8 -target 8 -classpath $androidJar -d $classes $source
    if ($LASTEXITCODE -ne 0) { throw "$AppName javac failed" }
    $classInputs = Get-ChildItem -Path $classes -Recurse -Filter '*.class' | Select-Object -ExpandProperty FullName
    & (Join-Path $buildTools 'd8.bat') --lib $androidJar --output $dex $classInputs
    if ($LASTEXITCODE -ne 0) { throw "$AppName d8 failed" }
    & jar uf $unsigned -C $dex classes.dex
    if ($LASTEXITCODE -ne 0) { throw "$AppName jar update failed" }
    & (Join-Path $buildTools 'zipalign.exe') -f 4 $unsigned $aligned
    if ($LASTEXITCODE -ne 0) { throw "$AppName zipalign failed" }
    if (-not (Test-Path $keystore)) {
        & keytool -genkeypair -keystore $keystore -storepass android -alias androiddebugkey -keypass android -dname 'CN=Android Debug,O=Android,C=US' -keyalg RSA -keysize 2048 -validity 10000
        if ($LASTEXITCODE -ne 0) { throw 'keytool failed' }
    }
    & (Join-Path $buildTools 'apksigner.bat') sign --min-sdk-version 26 --ks $keystore --ks-pass pass:android --key-pass pass:android $aligned
    if ($LASTEXITCODE -ne 0) { throw "$AppName apksigner failed" }
    Write-Output $aligned
}

Build-BinderApk -AppName 'binder-service' `
    -PackagePath 'benchmarks\android_binder_service_app' `
    -ManifestPath 'AndroidManifest.xml' `
    -ClassPath 'src\io\dros\tmc\binderfixture\BoundedFixtureService.java' `
    -OutputName 'dros-tmc-binder-service.apk'

Build-BinderApk -AppName 'binder-client' `
    -PackagePath 'benchmarks\android_binder_client_app' `
    -ManifestPath 'AndroidManifest.xml' `
    -ClassPath 'src\io\dros\tmc\binderclient\MainActivity.java' `
    -OutputName 'dros-tmc-binder-client.apk'
