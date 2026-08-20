# M245 dummy-only GREEN driver - executes the four exact I1.7 commands
# serially, once each, from the authority directory, capturing per-command
# UTC intervals, exit codes, and stdout/stderr. Stops on first failure.
$ErrorActionPreference = 'Stop'
$auth = 'C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\corpus\whestbench\experiments\m245_canonical_unordered_replica_galerkin_spectrum'
$py = 'C:\Users\strid\.venvs\whestbench-frozen-m178\Scripts\python.exe'
$log = 'C:\Users\strid\Documents\Codex\2026-08-02\https-chatgpt-com-share-6a5556ed-2e1c\publish\recursive-estimator-folding\tasks\m245-green-logs'
$tests = @(
    'test_m245_primary_core.py',
    'test_m245_replica_core.py',
    'test_m245_scientific_transport.py',
    'test_m245_aggregation.py'
)
$overall = 'GREEN_ALL_ZERO'
for ($i = 0; $i -lt 4; $i++) {
    $name = $tests[$i]
    $n = $i + 1
    $start = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'")
    $proc = Start-Process -FilePath $py `
        -ArgumentList @('-B', '-m', 'unittest', '-v', $name) `
        -WorkingDirectory $auth `
        -RedirectStandardOutput (Join-Path $log "cmd$n.out") `
        -RedirectStandardError (Join-Path $log "cmd$n.err") `
        -NoNewWindow -Wait -PassThru
    $exit = $proc.ExitCode
    $end = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss.fffffff'Z'")
    "$n|$name|$start|$end|$exit" | Add-Content -Encoding ascii (Join-Path $log 'progress.log')
    if ($exit -ne 0) {
        $overall = "FAIL_IMPLEMENTATION_GREEN_STOP_NO_RERUN command $n exit $exit"
        break
    }
}
$overall | Set-Content -Encoding ascii (Join-Path $log 'DONE')
