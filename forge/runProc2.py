#! /usr/bin/python

import os, time, sys, subprocess;

def GetNextCmd(FNm) :
  InF = open(FNm, 'rt')
  LineV = InF.readlines()
  InF.close()
  NewCmd = ''
  CmdId = 0
  while CmdId < len(LineV) :
    if LineV[CmdId].startswith('*** ') : break;
    CmdId += 1
  if CmdId >= len(LineV) : CmdId = 0
  else : CmdId += 1
  if CmdId > 0 : LineV[CmdId-1] = LineV[CmdId-1 ][4 :]
  # find next cmd
  while CmdId < len(LineV) and (len(LineV[CmdId].strip()) == 0 or LineV[CmdId][0] == '#') :
    CmdId += 1;
  if CmdId < len(LineV) :
    NewCmd = LineV[CmdId]
    LineV[CmdId] = '*** ' + NewCmd
  OutF = open(FNm, 'wt')
  for line in LineV : OutF.write(line)
  OutF.close();
  return NewCmd.strip()

def RunCmd(CmdStr, CmdId, MxProc) :
  TmStr = time.strftime("%H:%M:%S %d/%m", time.localtime());
  #print '  %02d: Execute [%s]:  %s' % (CmdId, TmStr, CmdStr.strip())
  BatFNm = 'xxxRunProc%d.sh' % ((CmdId%MxProc)+1);
  F = open(BatFNm, 'wt');
  F.write('#! /bin/sh\n')  
  F.write(CmdStr+'\nexit\n')
  F.close()
  os.chmod(BatFNm, 0777)
  #FullCmdStr = 'C:\\WINDOWS\\system32\\cmd.exe /c "start "%d] %s %s" /wait %s"' % (CmdId, TmStr, CmdStr, BatFNm)
  FullCmdStr = '/bin/sh ' + BatFNm;
  Process = subprocess.Popen(FullCmdStr, shell=True)
  return Process
  
def Main() :
  if len(sys.argv) < 2 :
    print 'runProc: usage runProcPy <CommandFile> <RunMxProcs>'
    return
  FNm = sys.argv[1]
  MxProc = 4;
  if len(sys.argv) >= 3 : MxProc = int(sys.argv[2])
  ProcV = []
  # init
  while len(ProcV) < MxProc :
    CmdStr = GetNextCmd(FNm)
    if len(CmdStr) == 0 : return
    ProcV.append(RunCmd(CmdStr, len(ProcV)+1, MxProc))
  # run  
  done = set()
  Tm1 = time.time()
  while len(done) < MxProc:
    for pid in range(0, len(ProcV)) :
      if pid in done:
        continue
      if ProcV[pid].poll() != None :
        if len(done) > 0:
          done.add(pid)
          continue
        CmdStr = GetNextCmd(FNm)
        if len(CmdStr) == 0:
          done.add(pid)
          continue
        ProcV[pid] = (RunCmd(CmdStr, pid+1, MxProc))
    time.sleep(1)
  Tm2 = time.time()
  TmStr = time.strftime("%H:%M:%S %d/%m", time.localtime())
  print '__done__ %s [%s] %.2f\n' % (str(MxProc),
                TmStr, Tm2-Tm1)
  
Main()
