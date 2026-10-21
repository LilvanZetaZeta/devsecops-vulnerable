pipeline {
    agent any

    environment {
        APP_URL = 'http://flask-app:5000'
        IMAGE_NAME = 'devsecops-flask:local'
    }

    stages {

        stage('Build') {
            steps {
                echo 'Preparando aplicación Flask...'

                sh '''
                    python3 -m pip --version
                    python3 -m py_compile app.py
                    docker build -t "$IMAGE_NAME" .
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Ejecutando pruebas unitarias...'

                sh '''
                    python3 -m unittest discover \
                        -s . -p "test_*.py" -v
                '''
            }
        }

        stage('Analyze') {
            steps {
                echo 'Analizando código con SonarQube...'

                script {
                    def scannerHome = tool 'SonarScanner'

                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Desplegando Flask en Docker...'

                sh '''
                    docker rm -f flask-app || true

                    docker run -d \
                        --name flask-app \
                        --network devsecops-net \
                        -p 127.0.0.1:5000:5000 \
                        "$IMAGE_NAME"

                    sleep 5

                    curl --fail "$APP_URL/hello?name=TEST"
                '''
            }
        }

        stage('Security Test') {
            steps {
                echo 'Ejecutando Dependency-Check...'

                dependencyCheck(
                    odcInstallation: 'DP-Check',
                    additionalArguments: '--scan . --format ALL --out . --nvdApiDelay 8000'
                )

                dependencyCheckPublisher(
                    pattern: '**/dependency-check-report.xml',
                    skipNoReportFiles: true
                )

                echo 'Ejecutando OWASP ZAP...'

                sh '''
                    docker rm -f zap-scan 2>/dev/null || true

                    docker volume create zap-reports

                    docker create \
                        --name zap-scan \
                        --network devsecops-net \
                        -v zap-reports:/zap/wrk \
                        ghcr.io/zaproxy/zaproxy:stable \
                        zap-baseline.py \
                        -t "$APP_URL/hello?name=TEST" \
                        -r zap_report.html \
                        -I

                    docker start -a zap-scan

                    docker cp zap-scan:/zap/wrk/zap_report.html ./zap_report.html

                    docker rm -f zap-scan
                '''
            }
        }
    }

    post {
        always {
            echo 'Guardando reportes...'

            archiveArtifacts(
                artifacts: '**/dependency-check-report.html, **/zap_report.html',
                allowEmptyArchive: true
            )
        }
    }
}