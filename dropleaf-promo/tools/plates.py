import cv2, numpy as np
P='plates/'; O='build/img/'
def clean(fn, tags, brackets, out, crop):
    im=cv2.imread(P+fn); m=np.zeros(im.shape[:2],np.uint8)
    for x0,y0,x1,y1 in tags: m[y0:y1,x0:x1]=255
    for x0,y0,x1,y1 in brackets:
        reg=im[y0:y1,x0:x1]; mn=reg.min(axis=2); mm=(mn>200).astype(np.uint8)*255
        m[y0:y1,x0:x1]|=mm
    m=cv2.dilate(m,np.ones((7,7),np.uint8))
    r=cv2.inpaint(im,m,9,cv2.INPAINT_TELEA)
    x0,y0,x1,y1=crop; cv2.imwrite(O+out, r[y0:y1,x0:x1], [cv2.IMWRITE_JPEG_QUALITY,95])
# stowed (y offset 380, scale 2)
S=lambda a,b,c,d:(a*2,b*2+380,c*2,d*2+380)
clean('p_0.6.png',[S(16,246,76,268)],[S(10,262,60,315),S(10,470,60,522),S(478,262,530,315),S(478,470,530,522)],'stowed.jpg',(0,610,1080,1590))
clean('p_3.0.png',[S(18,206,120,238)],[S(10,232,60,285),S(10,370,60,425),S(458,232,512,285),S(458,370,512,425)],'deployed.jpg',(0,610,1080,1590))
for fn,out,crop in [('p_8.3.png','detail.jpg',(0,260,1080,1240)),('p_12.6.png','lowpro.jpg',(0,180,1080,1160)),('p_13.6.png','small.jpg',(0,120,1080,1100))]:
    clean(fn,[(372,655,448,745)] if out=='detail.jpg' else [],[],out,crop)
