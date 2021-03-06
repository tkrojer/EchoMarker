import os,glob
import sys

def copy_and_rename(plateList,newFolder,minstrelDir):
    for plate in plateList:
        os.chdir(newFolder)
        if not os.path.isdir(plate[0]):
            os.mkdir(plate[0])
        os.chdir(plate[0])
        if plate[1][1:4].startswith('0'):
            subFolder = plate[1][2:4]
        else:
             subFolder = plate[1][1:4]
        if os.path.isdir(os.path.join(minstrelDir,subFolder,'plateID_'+plate[1])):
            all_subdirs = []
            for batch in glob.glob(os.path.join(minstrelDir,subFolder,'plateID_'+plate[1],'*')):
                all_subdirs.append(batch)
            latest_subdir = max(all_subdirs, key=os.path.getmtime)
        
            for wellNum in sorted(glob.glob(os.path.join(minstrelDir,subFolder,'plateID_'+plate[1],latest_subdir,'*'))):
#                print wellNum
                nr = wellNum[wellNum.rfind('/')+1:].split('_')[1]
                if nr in nr_dict:
                    print plate[0],nr_dict[nr],' -> convert to png, resize & copy images...'
                    for image in glob.glob(os.path.join(wellNum,'profileID_1','*ef.jpg')):
#                        print image
                        imagePath=image[:image.rfind('/')]
                        imageFile=image[image.rfind('/')+1:]
                        if imageFile.startswith('d1'):
#                            os.system('/bin/cp ' + image + ' '+ nr_dict[nr]+'a.png')
                            os.system('convert '+image+' -resize 25% '+nr_dict[nr]+'a.png')
                        if imageFile.startswith('d2'):
#                            os.system('/bin/cp ' + image + ' ' + nr_dict[nr] + 'c.png')
                            os.system('convert '+image+' -resize 25% '+nr_dict[nr]+'c.png')
                        if imageFile.startswith('d3'):
#                            os.system('/bin/cp ' + image + ' ' + nr_dict[nr] + 'd.png')
                            os.system('convert '+image+' -resize 25% '+nr_dict[nr]+'d.png')


def errorMessage(barcodeError):
    print barcodeError
    print 'usage: copy_and_rename_frmlx_images <barcode> <formulatrix_id>'
    print '       e.g.'
    print '       copy_and_rename_frmlx_images CI059765 2345'
    quit()


if __name__ == '__main__':
    newFolder = os.getcwd()

    nr_dict = {

        '1': 'A01', '2': 'A02', '3': 'A03', '4': 'A04', '5': 'A05', '6': 'A06', '7': 'A07', '8': 'A08', '9': 'A09',
        '10': 'A10', '11': 'A11', '12': 'A12',
        '13': 'B01', '14': 'B02', '15': 'B03', '16': 'B04', '17': 'B05', '18': 'B06', '19': 'B07', '20': 'B08',
        '21': 'B09', '22': 'B10', '23': 'B11', '24': 'B12',
        '25': 'C01', '26': 'C02', '27': 'C03', '28': 'C04', '29': 'C05', '30': 'C06', '31': 'C07', '32': 'C08',
        '33': 'C09', '34': 'C10', '35': 'C11', '36': 'C12',
        '37': 'D01', '38': 'D02', '39': 'D03', '40': 'D04', '41': 'D05', '42': 'D06', '43': 'D07', '44': 'D08',
        '45': 'D09', '46': 'D10', '47': 'D11', '48': 'D12',
        '49': 'E01', '50': 'E02', '51': 'E03', '52': 'E04', '53': 'E05', '54': 'E06', '55': 'E07', '56': 'E08',
        '57': 'E09', '58': 'E10', '59': 'E11', '60': 'E12',
        '61': 'F01', '62': 'F02', '63': 'F03', '64': 'F04', '65': 'F05', '66': 'F06', '67': 'F07', '68': 'F08',
        '69': 'F09', '70': 'F10', '71': 'F11', '72': 'F12',
        '73': 'G01', '74': 'G02', '75': 'G03', '76': 'G04', '77': 'G05', '78': 'G06', '79': 'G07', '80': 'G08',
        '81': 'G09', '82': 'G10', '83': 'G11', '84': 'G12',
        '85': 'H01', '86': 'H02', '87': 'H03', '88': 'H04', '89': 'H05', '90': 'H06', '91': 'H07', '92': 'H08',
        '93': 'H09', '94': 'H10', '95': 'H11', '96': 'H12'

    }



    minstrelDir = '/minstrel4/pub/fmlximages/WellImages'

    try:
        swissCIbarode = sys.argv[1]
        if not swissCIbarode.startswith('CI'):
            barcodeError = 'ERROR: this does not seem to be a SWISS CI barcode:',sys.argv[1]
            errorMessage(barcodeError)
        plateList = [ [sys.argv[1],sys.argv[2] ] ]
        copy_and_rename(plateList,newFolder,minstrelDir)
        print '\nAll done!\n'

    except IndexError:
        barcodeError = ''
        errorMessage(barcodeError)






