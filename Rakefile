require 'rake'

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

# task :supervisor-setup do
# end

desc "Starts C++ BFS (not Python BFS)"
task :start do
    # NOTE: Assumptions:
    # Create `bin` directory, which is a staging directory to run
    sh "mkdir -p bin/"
    Dir.chdir("bin/") do
        sh "cp -f ../python/* ."
        sh "cp ../app/libbfs/* ../app/cppbfs/* ."
        sh "cp ../../snap-python/swig-sw/_snap.so ../../snap-python/swig-sw/snap.py ."
        sh "cp ../snapw.config ." # override config File

        sh "python master.py"
    end

    # sh "curl -i http://ild1.stanford.edu:9102/start"
    # n(2) Copies stuff (3) Run master (4)
end

task :quit do
    sh "curl -i http://ild1.stanford.edu:9102/quit"
end


