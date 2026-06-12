pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "aabdulmoiz"
        IMAGE_NAME = "sentiment-api"
        APP_PORT = "5000"
        CONTAINER_NAME = "sentiment-test-container"
    }

    stages {
        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh """
                    docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable .
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 \
                        -v /tmp/sentiment-logs:/app/logs \
                        ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable
                    sleep 20
                """
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    docker run --rm --network host \
                        -e BASE_URL=http://localhost:5000 \
                        ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable \
                        sh -c "pip install pytest requests && pytest tests/test_api.py -v"
                """
            }
        }

        stage('UI Test') {
                steps {
                    sh """
                        docker run --rm --network host \
                            -v "\$PWD":/app \
                            -w /app \
                            -e BASE_URL=http://localhost:5000 \
                            --shm-size=2g \
                            selenium/standalone-chrome:latest sh -c "
                                pip install selenium pytest requests &&
                                pytest tests/test_ui.py -v
                            "
                    """
                }
            }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin

                        # Push unstable image
                        docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable

                        # Build and push stable image from stable-fallback branch
                        git fetch origin stable-fallback
git checkout FETCH_HEAD -- app.py
docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:stable .
docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:stable
git checkout HEAD -- app.py
                    """
                }
            }
        }

    stage('Deploy to Minikube') {
    steps {
        sh """
            export KUBECONFIG=/var/lib/jenkins/.kube/config
            kubectl apply -f k8s/pvc.yaml
            kubectl apply -f k8s/blue-deployment.yaml
            kubectl apply -f k8s/green-deployment.yaml
            kubectl apply -f k8s/service.yaml
            kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s
            kubectl rollout status deployment/sentiment-green-deployment --timeout=120s
        """
    }
}
    }

    post {
        always {
            sh "docker rm -f ${CONTAINER_NAME} || true"
        }
    }
}