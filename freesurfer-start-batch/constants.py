class BUCKETS:
    NIFTILIST='freesurfer-niftilists'
    FINISHED='freesurfer-finished'
    LOGS='freesurfer-logs'
    NIFTIS='nifti-upload'
    LICENSES='freesurfer-licenses'

class TABLES:
    NIFTIS='freesurfer-niftis'
    JOBS='freesurfer-jobs'
    LICENSES='freesurfer-license'

class BATCH:
    MNT_ROOT='/fs_mnt'
    FREESURFER_HOME='/fs_mnt/freesurfer/7.2.2'
    SUBJECTS_DIR_ROOT='/fs_mnt/subjects'
    JOB_DEFINITION='echofile_with_volume__halbeCPU4GBRAM'
    JOB_QUEUE='Fargate_Spot_Queue'

class ACCESS:
    AWS_ACCESS_KEY_ID='<KEY>'
    AWS_SECRET_ACCESS_KEY='<SECRET_KEY>'
