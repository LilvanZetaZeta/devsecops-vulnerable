pipeline {
    agent any // Se ejecuta en el entorno disponible (tu contenedor Jenkins)

    environment {
        // Definimos la URL donde se levantará la aplicación para que ZAP la escanee
        APP_URL = "http://localhost:5000"
    }

    stages {
        stage('Build') {
            steps {
                echo 'Preparando el entorno y dependencias de python'
                // Se instala Flask para que el código pueda ejecutarse
                sh 'pip3 install Flask --break-system-packages'
            }
        }

        stage('Test') {
            steps {
                echo 'Ejecutando pruebas básicas...'
                // Validación básica de sintaxis de Python para el app.py
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Analyze') {
            steps {
                echo 'Ejecutando el análisis de calidad y seguridad con SonarQube...'
                // 'SonarQube' debe coincidir con el nombre que le diste en Global Tool Configuration
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner -Dsonar.projectKey=app-vulnerable -Dsonar.sources=.'
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Desplegando la aplicación en el entorno de prueba...'
                // Levantamos la aplicación vulnerable en segundo plano para que ZAP la escanee
                sh 'nohup python3 app.py > flask_app.log 2>&1 &'
                // Pausa breve para asegurar que el servidor web levante correctamente
                sleep 5 
            }
        }

        stage('Security Test') {
            steps {
                echo 'Ejecutando OWASP Dependency-Check...'
                // Ejecución del plugin Dependency-Check, generando un reporte en HTML
                // 'DP-Check' debe coincidir con el nombre que pusiste en Global Tool Configuration
                dependencyCheck additionalArguments: '--scan . --format HTML', odcInstallation: 'DP-Check'
                
                echo 'Ejecutando OWASP ZAP...'
                // Invocamos a OWASP ZAP (mediante Docker) para hacer un análisis dinámico contra la app desplegada
                sh 'docker run --network="host" -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py -t ${APP_URL} -r zap_report.html || true'
            }
        }
    }

    post {
        always {
            echo 'Limpiando el entorno y guardando evidencias...'
            // Matamos el proceso de la aplicación Flask para no ocupar el puerto[cite: 1]
            sh 'pkill -f "python3 app.py" || true'
            // Guardamos los reportes generados para que puedas revisarlos y sacar las capturas
            archiveArtifacts artifacts: 'dependency-check-report.html, zap_report.html', allowEmptyArchive: true
        }
    }
}