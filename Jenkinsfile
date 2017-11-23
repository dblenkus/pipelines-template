throttle(["pipelines_template"]) {

    node {
        // NOTE: To avoid exceeding the maximum allowed shebang lenght when calling pip due very
        // long paths of Jenkins' workspaces, we need to set a shorter Tox's working directory path
        // More info: http://tox.readthedocs.io/en/latest/example/jenkins.html#avoiding-the-path-too-long-error-with-long-shebang-lines
        def tox_workdir = "${env.HOME}/.tox-${env.BUILD_TAG}"
        // extra arguments passed to Tox
        def tox_extra_args = ""
        if (env.BRANCH_NAME && env.BRANCH_NAME == "master" ||
            env.CHANGE_TARGET && env.CHANGE_TARGET == "master") {
            // NOTE: If we are building the "master" branch or a pull request against the "master"
            // branch, we allow installing pre-releases with the pip command.
            tox_extra_args += "--pre"
        }

        try {
            stage("Checkout") {
                // check out the same revision as this script is loaded from
                checkout scm
            }

            stage("Test") {
                withEnv(["PIPELINES_TEMPLATE_POSTGRESQL_USER=postgres",
                         "PIPELINES_TEMPLATE_POSTGRESQL_PORT=55460",
                         // set database name to a unique value
                         "PIPELINES_TEMPLATE_POSTGRESQL_NAME=${env.BUILD_TAG}",
                         "PIPELINES_TEMPLATE_REDIS_PORT=57000",
                         "PIPELINES_TEMPLATE_DOCKER_COMMAND=sudo docker",
                         // set number of parallel Django test processes to 2
                         "DJANGO_TEST_PROCESSES=2",
                         "TOX_WORKDIR=${tox_workdir}"]) {
                    // documentation, linters, packaging and extra environments are run first so
                    // that if any of them fails, developer will get the feedback right away
                    // (rather than having to wait for all ordinary tests to run)
                    sh "tox -e docs ${tox_extra_args}"

                    sh "tox -e linters ${tox_extra_args}"

                    sh "tox -e packaging ${tox_extra_args}"

                    sh "tox -e extra ${tox_extra_args}"

                    sh "echo 'Environment:' && python3.4 --version"
                    sh "tox -e py34 ${tox_extra_args}"
                }
            }

        } catch (e) {
            currentBuild.result = "FAILED"
            // report failures only when testing the "master" branch
            if (env.BRANCH_NAME == "master") {
                notifyFailed()
            }
            throw e
        } finally {
            // manually remove Tox's working directory since it is created outside Jenkins's
            // workspace
            sh "rm -rf ${tox_workdir}"
        }
    }
}

def notifyFailed() {
    slackSend(
        color: "#FF0000",
        message: "FAILED: Job ${env.JOB_NAME} (build #${env.BUILD_NUMBER}) ${env.BUILD_URL}"
    )
}
