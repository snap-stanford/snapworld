require 'rake'

HOSTNAME = `hostname`.strip()
USER = ENV['USER']
HOST_PORT = (`python python/config.py snapw.config master`).strip().split(':')

HOST = HOST_PORT[0]
PORT = HOST_PORT[1]

SLEEPTIME = 10
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
            puts "=" * 60
            sh2 "ssh ild#{i} \"#{cmd}\""
        end
    elsif HOST.include? "iln" or HOST.include? "10.79.15.11"
        for i in 1..17
            puts "=" * 60
            ii = "%.2i" % i
            sh2 "ssh iln#{ii} \"#{cmd}\""
        end
    end
end

def task_dsh2(cmd)
    if HOST.include? "ild"
        sh2 "seq -f '%02g' 1 2 | parallel ssh ild{} \"#{cmd}\""
    elsif HOST.include? "iln" or HOST.include? "10.79.15.11"
        sh2 "seq -f '%02g' 2 2 | parallel ssh iln{} \"#{cmd}\""
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
        sh "cd snap-python/; git pull; git checkout master; cd swig-sw/; make clean; make;"
    end
end

def pre_deploy_cleanup()
    sh "fs flushvolume -path ." # flush AFS cache
    cleanup = "rm -rf #{LFS}/supervisors/*; rm -rf #{LFS}/snapshot-*; rm -rf #{LFS}/master.log"
    task_dsh(cleanup)
end

def task_deploy()
    config_filepath = "snapw.config"

    # Create `bin` directory, which is a staging directory to run
    stage_dir = "bin/"
    sh "mkdir -p #{stage_dir}"

    sh "cp -f -p python/* #{stage_dir}"
    sh "cp app/libbfs/* app/cppbfs/* #{stage_dir}"
    sh "cp app/pybfs/* #{stage_dir}"
    sh "cp -p ../snap-python/swig-sw/_snap.so ../snap-python/swig-sw/snap.py #{stage_dir}"
    # override config File
    sh "cp #{config_filepath} #{stage_dir}"

    Dir.chdir("bin/") do
        sh "mkdir -p #{LFS}"
        sh "time python master.py 2>&1 | tee #{LFS}/master.log"
    end
end

desc "Run C++ BFS (not Python BFS)"
task :deploy do
    pre_deploy_cleanup()
    task_deploy()
end

task :start do
    task_start(HOST, PORT)
end


task :stop do
    task_stop(HOST, PORT)
end

task :test do
    begin
        pre_deploy_cleanup()
        sh "sleep #{SLEEPTIME} && rake start &"
        task_deploy()
    rescue
        sh2 "rake stop"
    end
    sh2 "rake cleanup"
    # sh "rm -rf bin/"
    
    sh2 "rake dshgrep[\"WARNING|ERROR|CRITICAL|traceback\"]"
end


task :cleanup do
    sh "ps x | egrep 'python|node' | grep -v grep | grep -v emacs | grep -v vim | awk '{print $1}'| xargs -r kill -SIGKILL"
    killcmd_sup = "ps x | egrep 'python|node' | grep -v grep | grep -v emacs | grep -v vim | awk '{print \\$1}'| xargs -r kill -SIGKILL"
    task_dsh(killcmd_sup)
end

# Example: $ rake dsh["pkill python"]
task :dsh, :cmd do |t, args|
    cmd = args.cmd
    task_dsh(cmd)
end

task :check do
    task_dsh("ps aux | grep python | grep ${USER} | grep -v grep")
end

task :dshgrep, :txt do |t, args|
    txt = args.txt
    task_dsh("egrep -I -i --include='*.log' -r '#{txt}' #{LFS}")
end


task :agglogs do

    task_dsh("rm -rf /tmp/agglogs_#{USER}/; mkdir -p /tmp/agglogs_#{USER}/")
    cmd = "find #{LFS}/supervisors/ -name '*.log' | parallel python ~/hanworks/snapworld/misc/parselog.py"
    task_dsh(cmd)

    sh2 "rm -rf #{LFS}/all_logs"
    sh2 "mkdir -p #{LFS}/all_logs"
    task_dsh("scp /tmp/agglogs_#{USER}/\*.log #{HOSTNAME}:#{LFS}/all_logs/")
    sh2 "cp -f #{LFS}/master.log #{LFS}/all_logs"
    sh2 "cat #{LFS}/all_logs/* | sort > #{LFS}/aggregated.log"

end

task :dulogs do
    task_dsh("find #{LFS}/supervisors/ -iname '*.log' -print0 | du -h --files0-from - -c -s | tail -1")
end

################################


task :benchmark1 do
    sh2 "rake benchmark0"
    sh2 "rm -rf   #{LFS}/fake_test"
    sh2 "mkdir -p #{LFS}/fake_test"

    Dir.chdir("misc/") do
        sh2 "python fake_super.py -p 1337"
    end
end

task :benchmark2 do
    cmd = "seq 8 | parallel python ~/hanworks/snapworld/misc/fake_worker.py -hp iln01.stanford.edu:1337 -f ~/file200.dat"

    # 17 - 2 + 1 = 16 supr machines
    sh2 "seq -f '%02g' 2 17 | parallel ssh iln{} \"#{cmd}\""
end

task :benchmark0 do
    cmd = "pkill python"
    sh2 "seq -f '%02g' 1 19 | parallel ssh iln{} \"#{cmd}\""
end

task :genhosts do
    puts `seq -f "iln%02g.stanford.edu:9200" -s "," 2 17`
end

task :catbrokerlogs do
    task_dsh("cat #{LFS}/**/broker.log")
end
