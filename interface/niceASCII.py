#!/bin/python
oldLOGO = '''

███╗   ███╗ ██████╗ ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗ ████████╗
████╗ ████║██╔═══██╗████╗  ██║██╔════╝╚██╗ ██╔╝██╔══██╗██╔═══██╗╚══██╔══╝
██╔████╔██║██║   ██║██╔██╗ ██║█████╗   ╚████╔╝ ██████╔╝██║   ██║   ██║   
██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══╝    ╚██╔╝  ██╔══██╗██║   ██║   ██║   
██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████╗   ██║   ██████╔╝╚██████╔╝   ██║   
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═════╝  ╚═════╝    ╚═╝
'''



LOGO = ['''
███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗
████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║
██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║
██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║
██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║
╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝
      CRYPTOCURRENCY  ASSET
''',
'''
                       .-'`/
                   .-'`  _/
               .-'`    _/
            .-'       /
         .-'         /
       .'           (
     .'       ,,////)
    .         __,-^/
   .        ey\($)(
   :               \ 
   :             _  \ 
   :            (____\ 
   :              (
   `          )-.__) 
    `              ) 
     `.           (
       `.          \\ 
         `-.        \\
            `-.      \_
               `'-.    \_
                   `'-.  \_
                       `'-.\\
''',
'''
██████╗  ██████╗ ████████╗
██╔══██╗██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║   ██║   
██╔══██╗██║   ██║   ██║   
██████╔╝╚██████╔╝   ██║   
╚═════╝  ╚═════╝    ╚═╝   
         WATCHER
''']

def sumHorizonASCII(Images, Voffset):
    assert(len(Images) == len(Voffset))
    heights = [ Voffset[I] + len(IMG.split('\n')) for I, IMG in enumerate(Images) ]
    widths = [ max([len(I) for I in IMG.split('\n')]) for IMG in Images ]
    FinalImage = []
    for l in range(max(heights)):
        line = ''
        for I, IMG in enumerate(Images):
            try:
                idx = l-Voffset[I]
                assert(idx > 0)
                contr = IMG.split('\n')[idx]
                
            except:
                contr = ''

            line += contr + ' ' * (widths[I] - len(contr))
        FinalImage.append(line)
    
    return '\n'.join(FinalImage)
    
if __name__ == '__main__':
    print(sumHorizonASCII(LOGO, [7,0,7]))
