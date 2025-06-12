class TABLES:
	NIFTIS='freesurfer-niftis'
	JOBS='freesurfer-jobs'
	MACHINES='freesurfer-machines'
	LICENSES='freesurfer-licenses'

class NIFTIS: # refers to table NIFTIS
    JOB_UUID_INDEX='job_uuid-index'
    JOB_UUID_ATTR='job_uuid'
    NIFTI_UUID_ATTR='nifti_uuid'
    NAME_ATTR='name'
    S3_KEY_ATTR='s3_key'


    USER_NAME='user_name'
    LOGS='logs'
    PATH='path'
    PATH_SAVE='path_save'
    UID_CLIENT='uid_client'
    SIZE='size'
    STATUS='status'

class JOBS:
    USER_SUB_INDEX='user_sub-index'
    JOB_UUID_ATTR='job_uuid'
    TIME_CREATED_ATTR='created'
    USER_SUB_ATTR='user_sub'
    EMAIL_ATTR='email'
    STATUS_ATTR='status'
    CHECKOUT_NUM_ATTR='checkout_num'
    CHECKOUT_PRICE_ATTR='checkout_price'
    MACHINE_UUID_ATTR='machine_uuid'
    FS_LICENSE_UUID_ATTR='fs_license_uuid'

class LICENSES:
    USER_SUB_INDEX='user_sub-index'
    USER_SUB_ATTR='user_sub'
    LABEL_ATTR='label'
    BLOB_ATTR='blob'
    UUID_ATTR='uuid'

class STATUS:
	AWAITING_UPLOAD='awaiting-upload'


class REGIONS:
    DEFAULT='eu-central-1'

class MACHINES:
    UUID_ATTR='uuid'
    ARCHITECTURE_ATTR='arch'
    RAM_ATTR='ram'
    OS_ATTR='os'
    FS_VERSION_ATTR='fs_version'
