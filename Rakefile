require 'rake'

USER = ENV['USER']
if USER == 'minghan'
    PORT = 9102
elsif USER == 'nkhadke'
    PORT = 8102
end

HOST = (`python python/config.py snapw.config master`).split(':')[0]
HOSTNAME = `hostname`

if HOST.include? "ild"
    SLEEPTIME = 5
elsif HOST.include? "iln"
    SLEEPTIME = 15
end

LFS = "/lfs/local/0/${USER}"

################################

def sh2(cmd)
    begin
        sh cmd
    rescue
    end
end

def task_dsh(cmd)
    if HOST.include? "ild"
        for i in 1..2
            sh2 "ssh ild#{i} \"#{cmd}\""
        end
    elsif HOST.include? "iln"
        for i in 1..9
            sh2 "ssh iln0#{i} \"#{cmd}\""
        end
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
        sh "git clone git@github.com:minghan/snap-python.git" unless File.exists?("snap-python")
        sh "cd snap-python/; git pull; git checkout master; cd swig-sw/; make;"
    end
end

def pre_deploy_cleanup()
    sh "fs flushvolume -path ." # flush AFS cache
    cleanup = "rm -rf #{LFS}/supervisors/*"
    task_dsh(cleanup)
end

def task_deploy()
    # NOTE: Assumptions:
    
    pre_deploy_cleanup()

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
        sh "mkdir -p #{LFS}"
        sh "time python master.py 2>&1 | tee #{LFS}/master.log"
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
        sh "sleep #{SLEEPTIME} && rake start &"
        sh "rake deploy"
    rescue
        sh2 "rake stop"
    end
    sh2 "rake cleanup"
    # sh "rm -rf bin/"
end


task :cleanup do
    sh "ps x | grep python | grep -v grep | grep -v emacs | grep -v vim | awk '{print $1}'| xargs -r kill -SIGKILL"
    killcmd_sup = "ps x | grep python | grep -v grep | grep -v emacs | grep -v vim | awk '{print \\$1}'| xargs -r kill -SIGKILL"
    task_dsh(killcmd_sup)
end

task :dsh do
    task_dsh(ARGV[1].to_s) # FIXME
end

task :check do
    task_dsh("ps aux | grep python | grep ${USER} | grep -v grep")
    task_dsh("grep -r 15966 #{LFS}")
end
