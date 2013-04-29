require 'rake'

PORT = 9102
HOST = "ild1.stanford.edu"
################################

def sh2(cmd)
    begin
        sh cmd
    rescue
    end
end


def task_start(host, port)
    sh "curl -i http://#{host}:#{port}/start"
end

def task_stop(host, port)
    sh "curl -i http://#{host}:#{port}/stop"
end

task :setup do
    # NOTE: Assumptions: This script will put stuff in parent directory.
    Dir.chdir("../") do
        sh "git clone git@github.com:snap-stanford/snap.git" unless File.exists?("snap")
        sh "cd snap/; git pull; git checkout master;"
        # NOTE: (1) snap-python requires snap to compie (2) we also need swig
        sh "git clone git@github.com:snap-stanford/snap-python.git" unless File.exists?("snap-python")
        sh "cd snap-python/; git pull; git checkout master; cd swig-sw/; make;"
    end
end

def task_deploy()
    # NOTE: Assumptions:
    
    cleanup = "rm -rf /lfs/local/0/${USER}/supervisors/*"
    for i in 1..2
        sh2 "ssh ild#{i} #{cleanup}"
    end

    config_filepath = "snapw.config"

    # Create `bin` directory, which is a staging directory to run
    stage_dir = "bin/"
    sh "mkdir -p #{stage_dir}"

    sh "cp -f python/* #{stage_dir}"
    sh "cp app/libbfs/* app/cppbfs/* #{stage_dir}"
    sh "cp app/pybfs/* #{stage_dir}"
    sh "cp ../snap-python/swig-sw/_snap.so ../snap-python/swig-sw/snap.py #{stage_dir}"
    # override config File
    sh "cp #{config_filepath} #{stage_dir}"

    Dir.chdir("bin/") do
        sh "time python master.py"
    end
end

desc "Run C++ BFS (not Python BFS)"
task :deploy do
    task_deploy()
end

task :start do
    task_start(HOST, PORT)
end


task :stop do
    task_stop(HOST, PORT)
end

task :test do
    # if ARGV[1].to_s == ''
        # config_filepath = "snapw.config"
    # else
        # config_filepath = ARGV[1]
    # end
    # host_port = `cd python; python -mconfig ../#{config_filepath} master`
    # host, port = host_port.split(":")

    begin
        sh "sleep 3 && rake start &"
        sh "rake deploy"
    rescue
        sh2 "rake stop"
    end
    sh2 "rake cleanup"
    # sh "rm -rf bin/"
end


task :cleanup do
    sh "ps x | grep python | grep master.py | grep -v grep | awk '{print $1}'| xargs --no-run-if-empty kill -SIGKILL"
    killcmd_sup = "ps x | grep python | grep supervisor.py | grep -v grep | awk '{print \\$1}'| xargs --no-run-if-empty kill -SIGKILL"
    for i in 1..2
        sh2 "ssh ild#{i} \"#{killcmd_sup}\""
    end
end
