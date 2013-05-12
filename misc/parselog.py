import sys, os
import commands

"""
Usage: python parselog.py oldlog.log
"""

def main():
    if len(sys.argv) < 2:
        print "Usage: python parselog.py <file>"
        sys.exit()

    hostname = commands.getoutput("hostname")
    user = os.environ['USER'].strip()
    host = hostname.split('.', 1)[0]

    input_filename = sys.argv[1]
    prefix = "/lfs/local/0/"
    if input_filename.startswith(prefix):
        input_filename2 = input_filename[len(prefix):]
    else:
        input_filename2 = input_filename
    output_filename = ("/tmp/agglogs_%s/" % user) + host + "+" + "_".join(input_filename2.split('/'))

    print "%s -> %s" % (input_filename, output_filename)

    fin = open(input_filename, 'r')
    f = open(output_filename, 'w')

    for line in fin:
        line = line.strip()
        if line == "": continue

        try:
            a = line.index(']')
            b = line.index(']', a+1)
            newline = "%s [%s]%s" % (line[:b+1], output_filename, line[b+1:])

            f.write(newline)
            f.write('\n')
        except:
            print "Cannot parse: %s" % line
    
    f.close()
    fin.close()

if __name__ == '__main__':
    main()

