require 'rake'

PORT = 8102
################################

def sh2(cmd)
    begin
        sh cmd
    rescue
    end
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

desc "Run C++ BFS (not Python BFS)"
task :deploy do
    # NOTE: Assumptions:
    
    cleanup = "rm -rf /lfs/local/0/${USER}/supervisors/*"
    for i in 1..2
        sh2 "ssh ild#{i} #{cleanup}"
    end

    # Create `bin` directory, which is a staging directory to run
    sh "mkdir -p bin/"
    Dir.chdir("bin/") do
        sh "cp -f ../python/* ."
        sh "cp ../app/libbfs/* ../app/cppbfs/* ."
        sh "cp ../app/pybfs/* ."
        sh "cp ../../snap-python/swig-sw/_snap.so ../../snap-python/swig-sw/snap.py ."
        sh "cp ../snapw.config ." # override config File

        sh "python master.py"
    end
end

task :start do
    sh "curl -i http://ild1.stanford.edu:#{PORT}/start"
end


task :stop do
    sh "curl -i http://ild1.stanford.edu:#{PORT}/quit"
end

task :test do
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
