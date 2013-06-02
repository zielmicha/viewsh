from viewsh import rc
from viewsh import comm

def main():
    gstate = comm.GlobalState()
    gstate[comm.Interface].patch_log()

    rc.main(0, gstate)

if __name__ == '__main__':
    main()
