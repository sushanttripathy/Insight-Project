__author__ = 'Sushant'
from ImageFeatureDetect import ImageFeatureDetect, ImageROI

import os

cwd = os.path.curdir
im_dir = os.path.join(cwd, "..", "data", "negatives")
det_path = os.path.join(cwd, "..", "data", "neg_detections")
start_range = 0
step = 250
end_range = start_range + step
det_count = 0
cur_det_dir = os.path.join(det_path, str(start_range)+"_"+str(end_range))
os.mkdir(cur_det_dir)
for file in os.listdir(im_dir):

    im_path  = os.path.join(im_dir, file)
    if os.path.isfile(im_path):
        print "Processing " + im_path

        ifd = ImageFeatureDetect(im_path, 400, 400, 1)
        ifd.resize_image(400, 400)

        #ifd.get_orientations_with_PCA()

        ifd.get_skin_mask_with_edge_detection()

        # ifd.rotate_image(90)


        cwd = os.path.curdir

        cascade_dir = os.path.join(cwd, "..", "extra", "cascades")

        face_cascade_1 = os.path.join(cascade_dir, "face", "haarcascade_frontalface_alt_tree.xml")
        #face_cascade_2 = os.path.join(cascade_dir, "face", "haarcascade_profileface.xml")
        #face_cascade_2 = os.path.join(cascade_dir, "face", "lbpcascade_frontalface.xml")
        face_cascade_2 = os.path.join(cascade_dir, "face", "haarcascade_frontalface_alt.xml")

        face_cascade_3 = os.path.join(cascade_dir, "face", "hogcascade_face_24x24_d3_s17.xml")

        breast_cascade_1 = os.path.join(cascade_dir, "breast", "haarcascade_breast.xml")
        breast_cascade_2 = os.path.join(cascade_dir, "breast", "hogcascade_breasts_36x36-d3_1_17.xml")

        bikini_top_cascade = os.path.join(cascade_dir, "bikini_top", "haarcascade_bikinitop_24x24_d2_s21.xml")

        midriff_cascade = os.path.join(cascade_dir, "midriff", "hogcascade_midriff_36x36-d3_1_17.xml")

        mons_pubis_cascade = os.path.join(cascade_dir, "mons_pubis", "hogcascade_32x32_d3_s11.xml")

        ifd.load_cascade(face_cascade_1)
        ifd.load_cascade(face_cascade_2)
        ifd.load_cascade(face_cascade_3)

        ifd.load_cascade(breast_cascade_1)
        ifd.load_cascade(breast_cascade_2)

        ifd.load_cascade(bikini_top_cascade)

        ifd.load_cascade(midriff_cascade)

        ifd.load_cascade(mons_pubis_cascade)

        ifd.detect_image_features()

        rois = ifd.get_detected_rois()

        face = []
        breast = []
        breasts = []
        bikini_top = []
        midriff = []
        mons_pubis = []

        for r in rois:
            # print r
            # print rois[r]
            if r == 0 or r == 1 or r == 2:
                face.extend(rois[r])
            elif r == 3:
                breast.extend(rois[r])
            elif r == 4:
                breasts.extend(rois[r])
            elif r == 5:
                bikini_top.extend(rois[r])
            elif r == 6:
                midriff.extend(rois[r])
            elif r == 7:
                mons_pubis.extend(rois[r])

        # Cull image rois based on skin content

        if ifd.is_color():
            for i, roi in enumerate(breast):
                if ifd.get_skin_fraction(roi) < 0.3:
                    breast.pop(i)
            for i, roi in enumerate(breasts):
                if ifd.get_skin_fraction(roi) < 0.3:
                    breasts.pop(i)
            for i, roi in enumerate(bikini_top):
                if ifd.get_skin_fraction(roi) < 0.1:
                    bikini_top.pop(i)
            for i, roi in enumerate(midriff):
                if ifd.get_skin_fraction(roi) < 0.3:
                    midriff.pop(i)
            for i, roi in enumerate(mons_pubis):
                if ifd.get_skin_fraction(roi) < 0.4:
                    mons_pubis.pop(i)

        # Convert ROIs into ImageROI objects

        face_objs = []
        breasts_objs = []
        bikini_top_objs = []
        midriff_objs = []
        mons_pubis_objs = []

        for roi in face:
            face_objs.append(ImageROI(roi))
        # haarcascade_breast output is not culled via overlap check
        for roi in breasts:
            breasts_objs.append(ImageROI(roi))
        for roi in bikini_top:
            bikini_top_objs.append(ImageROI(roi))
        for roi in midriff:
            midriff_objs.append(ImageROI(roi))
        for roi in mons_pubis:
            mons_pubis_objs.append(ImageROI(roi))

        #Cull ROIs based on overlap
        to_pop = []
        for i, roi_obj in enumerate(midriff_objs):
            #popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_area(face_roi_obj):
                    to_pop.append(i)
                    #popped_flag = 1
                    break

            #if popped_flag:
            #    continue
        new_midriff_objs = []
        for i, obj in enumerate(midriff_objs):
            if i not in to_pop:
                new_midriff_objs.append(obj)

        midriff_objs = new_midriff_objs


        to_pop = []

        for i, roi_obj in enumerate(breasts_objs):
            popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                    #breasts_objs.pop(i)
                    to_pop.append(i)
                    popped_flag = 1
                    break

            if popped_flag:
                continue

            for midriff_roi_obj in midriff_objs:
                if roi_obj.is_within_bounds(midriff_roi_obj.centroid()):
                    #breasts_objs.pop(i)
                    to_pop.append(i)
                    popped_flag = 1
                    break

        new_breasts_objs = []
        for i, obj in enumerate(breasts_objs):
            if i not in to_pop:
                new_breasts_objs.append(obj)
        breasts_objs = new_breasts_objs

        to_pop = []

        for i, roi_obj in enumerate(bikini_top_objs):
            popped_flag = 0
            print "Exploring : "
            print roi_obj.x, roi_obj.y, roi_obj.w, roi_obj.h
            for face_roi_obj in face_objs:
                print "Checking overlap"
                print face_roi_obj.x, face_roi_obj.y, face_roi_obj.w, face_roi_obj.h
                print "vs"
                print roi_obj.x, roi_obj.y, roi_obj.w, roi_obj.h
                print roi_obj.get_overlap_fraction(face_roi_obj)
                print "============================"
                if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                    print "Popping : "
                    print (roi_obj.x, roi_obj.y, roi_obj.w, roi_obj.h)
                    print i
                    print len(bikini_top_objs)
                    #bikini_top_objs.pop(i)
                    to_pop.append(i)
                    print len(bikini_top_objs)
                    popped_flag = 1
                    break

            if popped_flag:
                continue
            for midriff_roi_obj in midriff_objs:
                if roi_obj.is_within_bounds(midriff_roi_obj.centroid()):
                    #bikini_top_objs.pop(i)
                    to_pop.append(i)
                    popped_flag = 1
                    break

        new_bikini_tops_objs  = []
        for i, obj in enumerate(bikini_top_objs):
            if i not in to_pop:
                new_bikini_tops_objs.append(obj)

        bikini_top_objs = new_bikini_tops_objs

        for i, roi_obj in enumerate(mons_pubis_objs):
            #popped_flag = 0

            for face_roi_obj in face_objs:
                if roi_obj.get_overlap_fraction(face_roi_obj) > 0.2:
                    mons_pubis_objs.pop(i)
                    #popped_flag = 1
                    break

            #if popped_flag:
            #    continue

        #ifd.show_image_with_rois()

        #Select ROIs for blurring

        blur_rois = []

        for roi in breast:
            blur_rois.append(roi)
            #out_path = os.path.join(det_path, "breast", str(det_count)+".png")
            #det_count += 1
            #ifd.save_roi(roi, out_path)

        for roi_obj in breasts_objs:
            blur_rois.append(roi_obj.get_roi_tuple())
            #out_path = os.path.join(det_path, "breasts", str(det_count)+".png")
            #det_count += 1
            #ifd.save_roi(roi_obj.get_roi_tuple(), out_path)

        for roi_obj in bikini_top_objs:
            roi = roi_obj.get_roi_tuple()
            if ifd.get_skin_fraction(roi) > 0.5:
                blur_rois.append(roi)
                #out_path = os.path.join(det_path, "bikini_tops", str(det_count)+".png")
                #det_count += 1
                #ifd.save_roi(roi_obj.get_roi_tuple(), out_path)

        for roi_obj in mons_pubis_objs:
            blur_rois.append(roi_obj.get_roi_tuple())
            #out_path = os.path.join(det_path, "mons_pubis", str(det_count)+".png")
            #det_count += 1
            #ifd.save_roi(roi_obj.get_roi_tuple(), out_path)

        for roi in blur_rois:
            out_path = os.path.join(cur_det_dir, str(det_count)+".png")
            ifd.save_roi(roi, out_path)
            det_count += 1
            if det_count == end_range:
                end_range = end_range + step
                start_range = start_range + step
                cur_det_dir = os.path.join(det_path, str(start_range)+"_"+str(end_range))
                os.mkdir(cur_det_dir)

        #if len(blur_rois):
            #Blur the ROIs to be blurred
            #ifd.image_gaussian_blur(blur_rois, 200)
        #ifd.show_image()

        print "Initial detections : "
        print "Faces"
        print face

        print "Breasts"
        print breast
        print breasts

        print "Bikini Tops"
        print bikini_top

        print "Midriff"
        print midriff

        print "Mons pubis"
        print mons_pubis

        print "==========================="

        print "Faces :"
        for f in face_objs:
            f.print_vals()

        print "Breasts :"
        #print breast
        #print breasts
        for b in breasts_objs:
            b.print_vals()

        print "Bikini Top : "
        for b in bikini_top_objs:
            b.print_vals()

        print "Midriff :"
        #print midriff
        for m in midriff_objs:
            m.print_vals()

        print "Down Under :"
        #print mons_pubis
        for m in mons_pubis_objs:
            m.print_vals()