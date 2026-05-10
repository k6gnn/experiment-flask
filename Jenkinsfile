// -----------------------------------------------------------------------------
// Jenkinsfile - CI/CD Pipeline with Self-Healing Mechanisms M1-M14
// Python Flask equivalent of the original Java Spring Boot pipeline.
//
// M14 runs first as a warning-only proactive risk predictor.
// M13 runs last (post stage, always) as an ML-based failure classifier.
// -----------------------------------------------------------------------------

pipeline {

    agent none  // Each stage declares its own agent/image

    // -------------------------------------------------------------------------
    // Global environment variables  (M9 verifies these are all set)
    // -------------------------------------------------------------------------
    environment {
        PYTHON_VERSION         = '3.11'
        APP_NAME               = 'grade-management'
        BUILD_TIMEOUT_MINUTES  = '10'
        TEST_TIMEOUT_MINUTES   = '10'
        MAX_RETRIES            = '2'
        M14_THRESHOLD_MODE     = 'balanced'
        M14_MODE               = 'warning_only'
        PIP_CACHE_DIR          = "${WORKSPACE}/.cache/pip"
    }

    options {
        // Discard old builds - keep 30 days of artifacts, last 20 builds
        buildDiscarder(logRotator(daysToKeepStr: '30', numToKeepStr: '20'))
        timestamps()
        ansiColor('xterm')
    }

    stages {

        // =====================================================================
        // STAGE: Risk Assessment  (M14)
        // Warning-only - never blocks the pipeline.
        // =====================================================================
        stage('M14 - Risk Assessment') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                script {
                    try {
                        sh '''
                            echo "=== M14: Proactive Failure Risk Assessment ==="
                            export HOME=/tmp
                            python -m pip install --upgrade pip -q --user
                            pip install -q numpy scikit-learn joblib requests --user
                            export PYTHONPATH=$(python -c "import site; print(site.getusersitepackages())")
                            export PATH="$HOME/.local/bin:$PATH"

                            if [ ! -f "scripts/m14_predict.py" ] || \
                               [ ! -f "models/m14_model.pkl" ]   || \
                               [ ! -f "models/m14_config.pkl" ]; then
                                echo "WARNING: M14 model files not found - skipping prediction (warning-only mode)"
                                echo \'{"status":"skipped","reason":"model_files_not_found","risk_score":0,"risk_level":"unknown","warning":false}\' > m14_risk_report.json
                                cat m14_risk_report.json
                                exit 0
                            fi

                            python scripts/m14_predict.py \
                                --platform  jenkins \
                                --repository "${JOB_NAME}" \
                                --commit     "${GIT_COMMIT}" \
                                --branch     "${GIT_BRANCH}" \
                                --event      "push" \
                                --model      models/m14_model.pkl \
                                --config     models/m14_config.pkl \
                                --output     m14_risk_report.json

                            cat m14_risk_report.json
                        '''
                    } catch (err) {
                        // allow_failure: true equivalent — M14 never blocks the pipeline
                        echo "M14 risk assessment failed (non-blocking): ${err.message}"
                        sh "echo '{\"status\":\"error\",\"reason\":\"assessment_failed\"}' > m14_risk_report.json"
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'm14_risk_report.json', allowEmptyArchive: true
                    stash name: 'm14-report', includes: 'm14_risk_report.json', allowEmpty: true
                }
            }
        }

        // =====================================================================
        // STAGE: Pre-Pipeline  (M9 + M8)
        // =====================================================================
        stage('Pre-Pipeline') {
            agent {
                docker { image 'ubuntu:22.04' }
            }
            options {
                timeout(time: 4, unit: 'MINUTES')
            }
            stages {

                // -------------------------------------------------------------
                // M9 - Environment Variable Verification
                // -------------------------------------------------------------
                stage('M9 - Environment Verification') {
                    steps {
                        sh '''
                            echo "=== M9 Environment Variable Verification ==="

                            check_var() {
                                name="$1"
                                value="$2"
                                if [ -z "$value" ]; then
                                    echo "MISSING: $name"
                                    return 1
                                else
                                    echo "OK: $name = $value"
                                    return 0
                                fi
                            }

                            MISSING=0
                            check_var "PYTHON_VERSION"        "$PYTHON_VERSION"        || MISSING=$((MISSING+1))
                            check_var "APP_NAME"              "$APP_NAME"              || MISSING=$((MISSING+1))
                            check_var "BUILD_TIMEOUT_MINUTES" "$BUILD_TIMEOUT_MINUTES" || MISSING=$((MISSING+1))
                            check_var "TEST_TIMEOUT_MINUTES"  "$TEST_TIMEOUT_MINUTES"  || MISSING=$((MISSING+1))

                            if [ "$MISSING" -gt 0 ]; then
                                echo "FAILURE: $MISSING required variable(s) are missing."
                                exit 1
                            fi

                            echo "All environment variables verified successfully."
                        '''
                    }
                }

                // -------------------------------------------------------------
                // M8 - Configuration Validation Gate
                // -------------------------------------------------------------
                stage('M8 - Configuration Validation') {
                    steps {
                        sh '''
                            echo "=== M8 Configuration Validation Gate ==="

                            echo "--- Validating requirements.txt ---"
                            if [ ! -f "requirements.txt" ]; then
                                echo "FAILURE: requirements.txt not found"
                                exit 1
                            fi

                            for pkg in "Flask" "Flask-SQLAlchemy" "marshmallow" "pytest"; do
                                if grep -qi "^${pkg}" requirements.txt; then
                                    echo "OK: $pkg found in requirements.txt"
                                else
                                    echo "FAILURE: $pkg missing from requirements.txt"
                                    exit 1
                                fi
                            done

                            echo "--- Validating app/__init__.py configuration ---"
                            if [ ! -f "app/__init__.py" ]; then
                                echo "FAILURE: app/__init__.py not found"
                                exit 1
                            fi

                            for key in "SQLALCHEMY_DATABASE_URI" "APP_NAME" "SERVER_PORT"; do
                                if grep -q "$key" app/__init__.py; then
                                    echo "OK: $key found in app config"
                                else
                                    echo "FAILURE: Required config key '$key' missing"
                                    exit 1
                                fi
                            done

                            echo "Configuration validation passed."
                        '''
                    }
                }
            }
        }

        // =====================================================================
        // STAGE: Build  (M1, M2, M3, M11)
        // =====================================================================
        stage('Build') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            options {
                timeout(time: 10, unit: 'MINUTES')
                retry(2)    // M1 - automatic retry on failure
            }
            steps {
                // M11 - pip dependency cache via Jenkins cache plugin
                cache(maxCacheSize: 512, caches: [
                    arbitraryFileCache(
                        path: '.cache/pip',
                        cacheValidityDecidingFile: 'requirements.txt'
                    )
                ]) {
                    sh '''
                        echo "=== Stage 1: Build ==="
                        export HOME=/tmp
                        export PIP_CACHE_DIR=".cache/pip"

                        if [ -d ".cache/pip" ]; then
                            echo "M11: Cache present - using cached dependencies"
                        else
                            echo "M11: Cache absent - downloading fresh dependencies"
                        fi

                        python -m pip install --upgrade pip > build.log 2>&1
                        pip install -r requirements.txt >> build.log 2>&1 || {
                            EXIT_CODE=$?
                            echo "M2: Primary install failed, attempting fallback without version pins..."
                            pip install Flask Flask-SQLAlchemy Flask-Marshmallow marshmallow-sqlalchemy pytest pytest-cov >> build.log 2>&1
                            EXIT_CODE=$?
                            cat build.log
                            exit $EXIT_CODE
                        }

                        python -c "from app import create_app; app = create_app(); print('OK: app factory loaded')" >> build.log 2>&1 || {
                            EXIT_CODE=$?
                            cat build.log
                            exit $EXIT_CODE
                        }

                        cat build.log
                        echo "Build completed successfully."
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'build.log', allowEmptyArchive: true
                    stash name: 'build-log', includes: 'build.log', allowEmpty: true
                }
                failure {
                    // M3 - Build failure notification
                    echo "=== M3: Build Failure Notification ==="
                    echo "Branch:   ${env.GIT_BRANCH}"
                    echo "Commit:   ${env.GIT_COMMIT}"
                    echo "Build:    ${env.BUILD_URL}"
                    echo "ACTION REQUIRED: Build failed after retries."
                }
            }
        }

        // =====================================================================
        // STAGE: Test  (M4, M5, M6)
        // =====================================================================
        stage('Test') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            options {
                timeout(time: 10, unit: 'MINUTES')
                retry(2)    // M4 - automatic retry (flaky test resilience)
            }
            steps {
                cache(maxCacheSize: 512, caches: [
                    arbitraryFileCache(
                        path: '.cache/pip',
                        cacheValidityDecidingFile: 'requirements.txt'
                    )
                ]) {
                    sh '''
                        echo "=== Stage 2: Test ==="
                        export HOME=/tmp
                        export PIP_CACHE_DIR=".cache/pip"

                        pip install -r requirements.txt -q

                        mkdir -p test-results

                        python -m pytest tests/ \
                            --tb=short \
                            --junitxml=test-results/junit.xml \
                            -v > test.log 2>&1 || {
                            EXIT_CODE=$?
                            TIMESTAMP=$(date -u +%H:%M:%S)
                            echo "ATTEMPT_FAILED at $TIMESTAMP (exit_code=$EXIT_CODE)" >> flaky_failure_log.txt
                            grep -h "FAILED\\|ERROR\\|Exception\\|AssertionError" test.log 2>/dev/null \
                                >> flaky_failure_log.txt || true
                            cat test.log
                            exit $EXIT_CODE
                        }
                        cat test.log
                        touch flaky_failure_log.txt
                    '''
                }
            }
            post {
                always {
                    // M6 - JUnit test trend analysis (Jenkins native)
                    junit testResults: 'test-results/junit.xml', allowEmptyResults: true

                    sh '''
                        echo "=== M5: Flaky Test Quarantine Analysis ==="
                        JUNIT="test-results/junit.xml"
                        FLAG_FILE="flaky_failure_log.txt"

                        if [ -f "$FLAG_FILE" ] && [ -s "$FLAG_FILE" ] && [ -f "$JUNIT" ]; then
                            echo "M5: FLAKY TEST DETECTED"
                            cat "$FLAG_FILE"
                            echo "Classification: FLAKY CANDIDATE"
                            echo "Recommended action: quarantine the failing test from the critical path."
                        elif [ -f "$FLAG_FILE" ] && [ -s "$FLAG_FILE" ]; then
                            echo "M5: TEST FAILURES DETECTED (deterministic - not flaky)"
                            cat "$FLAG_FILE"
                        else
                            echo "M5: All tests passed - no flaky test candidates detected"
                        fi

                        echo "=== M6: Test Result Trend Analysis ==="
                        if [ -f "$JUNIT" ]; then
                            python3 -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('$JUNIT')
    root = tree.getroot()
    suite = root if root.tag == 'testsuite' else root.find('testsuite')
    if suite is None: suite = root
    total  = int(suite.get('tests', 0))
    failed = int(suite.get('failures', 0))
    errors = int(suite.get('errors', 0))
    passed = total - failed - errors
    print(f'Tests run: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors}')
    if failed > 0 or errors > 0:
        print('TREND ALERT: Test failures detected.')
    else:
        print('TREND OK: All tests passed in this run.')
except Exception as e:
    print(f'Could not parse JUnit XML: {e}')
" || true
                        else
                            echo "No JUnit report found - check test.log"
                        fi
                    '''

                    archiveArtifacts artifacts: 'test.log, flaky_failure_log.txt', allowEmptyArchive: true
                    archiveArtifacts artifacts: 'test-results/**', allowEmptyArchive: true
                    stash name: 'test-artifacts',
                          includes: 'test.log,flaky_failure_log.txt',
                          allowEmpty: true
                }
            }
        }

        // =====================================================================
        // STAGE: Package  (M10, M12)
        // =====================================================================
        stage('Package') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                cache(maxCacheSize: 512, caches: [
                    arbitraryFileCache(
                        path: '.cache/pip',
                        cacheValidityDecidingFile: 'requirements.txt'
                    )
                ]) {
                    sh '''
                        echo "=== Stage 3: Package ==="
                        export HOME=/tmp
                        pip install build wheel -q

                        python -m build --wheel --outdir dist/

                        WHEEL=$(find dist -name "*.whl" | head -1)
                        if [ -z "$WHEEL" ]; then
                            echo "FAILURE: No wheel artifact found in dist/"
                            exit 1
                        fi
                        echo "Wheel artifact produced: $WHEEL"
                        ls -lh "$WHEEL"
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dist/*.whl', allowEmptyArchive: true
                    stash name: 'wheel-artifact', includes: 'dist/*.whl', allowEmpty: true
                }
            }
        }

        // =====================================================================
        // STAGE: Deploy  (M7, M12)
        // Only runs on the main branch.
        // =====================================================================
        stage('Deploy') {
            // M7 - only deploy from main
            when {
                branch 'main'
            }
            agent {
                docker { image 'python:3.11-slim' }
            }
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                unstash 'wheel-artifact'
                sh '''
                    echo "=== Stage 4: Deploy ==="
                    WHEEL=$(find dist -name "*.whl" | head -1)
                    echo "Deploying artifact: $WHEEL"
                    echo "Build:  ${BUILD_NUMBER}"
                    echo "Commit: ${GIT_COMMIT}"
                    echo "Deployment successful."
                '''
            }
            post {
                failure {
                    // M7 - Automated rollback notification
                    sh '''
                        echo "=== M7: Automated Rollback Initiated ==="
                        echo "Deployment failed. In production this would revert to the last known good state."
                        git log --oneline -5 || true
                    '''
                }
            }
        }

    }   // end stages

    // =========================================================================
    // POST (always)  -  M13: ML Failure Classification
    // Runs after all stages regardless of pipeline outcome.
    // =========================================================================
    post {
        always {
            node('built-in') {
                script {
                    docker.image('python:3.11-slim').inside {
                        try { unstash 'm14-report'     } catch (e) { echo "No M14 report stash: ${e.message}" }
                        try { unstash 'build-log'      } catch (e) { echo "No build-log stash: ${e.message}" }
                        try { unstash 'test-artifacts' } catch (e) { echo "No test-artifacts stash: ${e.message}" }

                        sh """
                            echo "=== M13: ML Failure Classification ==="
                            export HOME=/tmp
                            python -m pip install --upgrade pip -q --user
                            pip install -q pandas numpy scikit-learn joblib --user
                            export PYTHONPATH=\$(python -c "import site; print(site.getusersitepackages())")
                            export PATH="\$HOME/.local/bin:\$PATH"

                            mkdir -p logs
                            [ -f build.log ]             && cp build.log             logs/build.log             || true
                            [ -f test.log ]              && cp test.log              logs/test.log              || true
                            [ -f flaky_failure_log.txt ] && cp flaky_failure_log.txt logs/flaky_failure_log.txt || true

                            cat > pipeline_status.json << 'ENDJSON'
{
  "platform":    "jenkins",
  "job_name":    "${env.JOB_NAME}",
  "build_number":"${env.BUILD_NUMBER}",
  "build_url":   "${env.BUILD_URL}",
  "commit":      "${env.GIT_COMMIT ?: 'unknown'}",
  "branch":      "${env.GIT_BRANCH ?: 'unknown'}",
  "result":      "${currentBuild.currentResult}"
}
ENDJSON
                            cat pipeline_status.json

                            if [ ! -f "scripts/m13_predict.py" ] || [ ! -f "models/m13_model_bundle.pkl" ]; then
                                echo "WARNING: M13 model files not found - skipping ML classification"
                                echo '{"status":"skipped","reason":"model_files_not_found"}' > m13_classification_report.json
                                cat m13_classification_report.json
                            else
                                python scripts/m13_predict.py \\
                                    --status pipeline_status.json \\
                                    --logs   logs \\
                                    --model-bundle models/m13_model_bundle.pkl \\
                                    --output m13_classification_report.json
                                cat m13_classification_report.json
                            fi

                            [ -f m14_risk_report.json ] || echo '{"status":"not_available"}' > m14_risk_report.json
                        """

                        archiveArtifacts artifacts: '''
                            m13_classification_report.json,
                            pipeline_status.json,
                            m14_risk_report.json,
                            logs/**
                        ''', allowEmptyArchive: true
                    }   // end docker.image().inside
                }
            }
        }
    }

}
