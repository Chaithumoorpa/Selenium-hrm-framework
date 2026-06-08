// ============================================================================
// Enterprise Selenium HRM Framework — Jenkins Multibranch Pipeline
// ============================================================================
// Pipeline Stages:
//   1. Checkout
//   2. Environment Validation
//   3. Install Dependencies
//   4. Code Quality (Lint + Format Check)
//   5. Test Execution (Smoke / Regression / BDD)
//   6. Report Generation (Allure)
//   7. Docker Build & Push
//   8. Kubernetes Deploy
//   9. Notifications (Slack)
// ============================================================================

def runCmd(String cmd) {
    if (isUnix()) {
        sh cmd
    } else {
        bat cmd
    }
}

def sendSlackNotification(String color, String message) {
    try {
        slackSend(channel: env.SLACK_CHANNEL, color: color, message: message)
    } catch (NoSuchMethodError e) {
        echo "Slack Notification plugin is not installed. Message summary: ${message}"
    } catch (Exception e) {
        echo "Failed to send Slack notification: ${e.getMessage()}"
    }
}

pipeline {
    agent any

    environment {
        ENV              = "${params.ENVIRONMENT ?: 'dev'}"
        BROWSER          = "${params.BROWSER ?: 'chrome'}"
        ALLURE_RESULTS   = 'reports/allure-results'
        DOCKER_IMAGE     = 'selenium-hrm-framework'
        DOCKER_REGISTRY  = "${env.DOCKER_REGISTRY ?: 'your-registry.com'}"
        SLACK_CHANNEL    = '#qa-alerts'
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'prod'], description: 'Target environment')
        choice(name: 'BROWSER', choices: ['chrome', 'firefox', 'edge'], description: 'Browser for execution')
        choice(name: 'TEST_SUITE', choices: ['smoke', 'regression', 'bdd', 'all'], description: 'Test suite to run')
        booleanParam(name: 'PUBLISH_DOCKER', defaultValue: false, description: 'Build and push Docker image')
        booleanParam(name: 'DEPLOY_K8S', defaultValue: false, description: 'Deploy to Kubernetes')
    }

    options {
        timestamps()
        timeout(time: 2, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '20'))
        disableConcurrentBuilds()
    }

    stages {

        stage('📋 Checkout') {
            steps {
                checkout scm
                script {
                    if (isUnix()) {
                        sh 'git log -1 --format="%H %s" | head -1'
                    } else {
                        bat 'git log -1 --format="%%H %%s"'
                    }
                }
                echo "Branch: ${env.BRANCH_NAME} | Commit: ${env.GIT_COMMIT}"
            }
        }

        stage('🔍 Environment Validation') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            echo "=== Environment Validation ==="
                            python3 --version
                            pip3 --version
                            echo "ENV: ${ENV}"
                            echo "BROWSER: ${BROWSER}"
                            echo "WORKSPACE: ${WORKSPACE}"
                        '''
                    } else {
                        bat '''
                            echo "=== Environment Validation ==="
                            python --version
                            pip --version
                            echo ENV: %ENV%
                            echo BROWSER: %BROWSER%
                            echo WORKSPACE: %WORKSPACE%
                        '''
                    }
                }
            }
        }

        stage('📦 Install Dependencies') {
            steps {
                script {
                    if (isUnix()) {
                        sh '''
                            pip3 install --upgrade pip --quiet
                            pip3 install -r requirements.txt --quiet
                            echo "✅ Dependencies installed"
                        '''
                    } else {
                        bat '''
                            python -m pip install --upgrade pip --quiet
                            pip install -r requirements.txt --quiet
                            echo "Dependencies installed"
                        '''
                    }
                }
            }
        }

        stage('🎨 Code Quality') {
            parallel {
                stage('Flake8 Lint') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh '''
                                    flake8 pages/ tests/ utilities/ locators/ step_definitions/ \
                                        --max-line-length=120 \
                                        --exclude=__pycache__ \
                                        --format=default \
                                        --count \
                                        --statistics
                                '''
                            } else {
                                bat '''
                                    flake8 pages/ tests/ utilities/ locators/ step_definitions/ ^
                                        --max-line-length=120 ^
                                        --exclude=__pycache__ ^
                                        --format=default ^
                                        --count ^
                                        --statistics
                                '''
                            }
                        }
                    }
                }
                stage('Black Format Check') {
                    steps {
                        script {
                            runCmd 'black pages/ tests/ utilities/ locators/ --check --line-length=120'
                        }
                    }
                }
            }
        }

        stage('🧪 Test Execution') {
            steps {
                script {
                    def suite = params.TEST_SUITE ?: 'smoke'
                    def marker = suite == 'all' ? 'not flaky' : suite
                    def bdd = suite == 'bdd' || suite == 'all'

                    withEnv(["ENV=${ENV}", "BROWSER=${BROWSER}", "HEADLESS=true"]) {
                        if (bdd) {
                            if (isUnix()) {
                                sh """
                                    behave features/ \
                                        --no-capture \
                                        --format allure_behave.formatter:AllureFormatter \
                                        -o ${ALLURE_RESULTS} || true
                                """
                            } else {
                                bat """
                                    behave features/ ^
                                        --no-capture ^
                                        --format allure_behave.formatter:AllureFormatter ^
                                        -o ${ALLURE_RESULTS} || true
                                """
                            }
                        }

                        if (suite != 'bdd') {
                            if (isUnix()) {
                                sh """
                                    pytest tests/ \
                                        -m "${marker}" \
                                        --alluredir=${ALLURE_RESULTS} \
                                        --tb=short \
                                        -v \
                                        --timeout=120 \
                                        -n 2 \
                                        --reruns=2 \
                                        --reruns-delay=3 \
                                        --junit-xml=reports/junit/results.xml \
                                    || true
                                """
                            } else {
                                bat """
                                    pytest tests/ ^
                                        -m "${marker}" ^
                                        --alluredir=${ALLURE_RESULTS} ^
                                        --tb=short ^
                                        -v ^
                                        --timeout=120 ^
                                        -n 2 ^
                                        --reruns=2 ^
                                        --reruns-delay=3 ^
                                        --junit-xml=reports/junit/results.xml ^
                                    || true
                                """
                            }
                        }
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit/results.xml'
                }
            }
        }

        stage('📊 Allure Report') {
            steps {
                script {
                    try {
                        allure([
                            includeProperties: true,
                            jdk: '',
                            properties: [],
                            reportBuildPolicy: 'ALWAYS',
                            results: [[path: 'reports/allure-results']]
                        ])
                    } catch (NoSuchMethodError e) {
                        echo "Allure Jenkins plugin is not installed. Skipping report generation step."
                    } catch (Exception e) {
                        echo "Failed to generate Allure report: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('🐳 Docker Build & Push') {
            when {
                anyOf {
                    branch 'main'
                    branch 'release/*'
                    expression { params.PUBLISH_DOCKER }
                }
            }
            steps {
                script {
                    def image = "${DOCKER_REGISTRY}/${DOCKER_IMAGE}"
                    def tag = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}".replace('/', '-')

                    try {
                        withCredentials([usernamePassword(
                            credentialsId: 'docker-registry-creds',
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )]) {
                            if (isUnix()) {
                                sh """
                                    docker login ${DOCKER_REGISTRY} -u ${DOCKER_USER} -p ${DOCKER_PASS}
                                    docker build -t ${image}:${tag} -t ${image}:latest .
                                    docker push ${image}:${tag}
                                    docker push ${image}:latest
                                    echo "✅ Docker image pushed: ${image}:${tag}"
                                """
                            } else {
                                bat """
                                    docker login ${DOCKER_REGISTRY} -u %DOCKER_USER% -p %DOCKER_PASS%
                                    docker build -t ${image}:${tag} -t ${image}:latest .
                                    docker push ${image}:${tag}
                                    docker push ${image}:latest
                                    echo Docker image pushed: ${image}:${tag}
                                """
                            }
                        }
                    } catch (Exception e) {
                        echo "Docker build and push failed or credentials missing. Error: ${e.getMessage()}"
                    }
                }
            }
        }

        stage('☸️ Kubernetes Deploy') {
            when {
                expression { params.DEPLOY_K8S && env.BRANCH_NAME == 'main' }
            }
            steps {
                script {
                    try {
                        withKubeConfig([credentialsId: 'k8s-kubeconfig']) {
                            if (isUnix()) {
                                sh '''
                                    kubectl apply -f k8s/ --namespace=selenium-hrm
                                    kubectl rollout status deployment/selenium-hrm-runner -n selenium-hrm
                                    echo "✅ Kubernetes deployment complete"
                                '''
                            } else {
                                bat '''
                                    kubectl apply -f k8s/ --namespace=selenium-hrm
                                    kubectl rollout status deployment/selenium-hrm-runner -n selenium-hrm
                                    echo Kubernetes deployment complete
                                '''
                            }
                        }
                    } catch (Exception e) {
                        echo "Kubernetes deployment skipped or failed. Error: ${e.getMessage()}"
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'logs/*.log, resources/screenshots/*.png', allowEmptyArchive: true
            cleanWs()
        }
        success {
            script {
                sendSlackNotification('good', """✅ *BUILD SUCCESS* — Selenium HRM Framework
Branch: `${env.BRANCH_NAME}` | Build: `#${env.BUILD_NUMBER}`
Suite: `${params.TEST_SUITE}` | Env: `${params.ENVIRONMENT}`
<${env.BUILD_URL}allure/|📊 Allure Report> | <${env.BUILD_URL}|🔗 Build>""")
            }
        }
        failure {
            script {
                sendSlackNotification('danger', """❌ *BUILD FAILED* — Selenium HRM Framework
Branch: `${env.BRANCH_NAME}` | Build: `#${env.BUILD_NUMBER}`
<${env.BUILD_URL}console|📋 Console Log> | <${env.BUILD_URL}|🔗 Build>""")
            }
        }
        unstable {
            script {
                sendSlackNotification('warning', """⚠️ *BUILD UNSTABLE* — Some tests failed
Branch: `${env.BRANCH_NAME}` | Build: `#${env.BUILD_NUMBER}`
<${env.BUILD_URL}allure/|📊 Allure Report>""")
            }
        }
    }
}
