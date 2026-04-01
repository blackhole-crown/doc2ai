// Vue 应用
new Vue({
    el: '#app',
    data() {
        return {
            // 输入方式
            inputMethod: 'path',
            folderPath: '',
            
            // 文件上传
            fileList: [],
            uploadUrl: '/api/upload',
            uploadTaskId: null,
            uploadProgress: 0,
            uploadStatus: null,
            uploadMessage: '',
            
            // 处理状态
            processing: false,
            result: null,
            previewTree: null,
            
            // UI 状态
            showConfig: false,
            showHelp: false,
            showRawJson: false,
            
            // 配置
            config: {
                processing: {
                    max_file_size_mb: 10,
                    exclude_patterns: ['.git', '__pycache__', 'node_modules', '.DS_Store', '*.pyc']
                },
                analysis: {
                    max_line_count: 500,
                    truncate_mode: 'head_tail',
                    head_lines: 100,
                    tail_lines: 50
                },
                output: {
                    format: 'detailed'
                }
            },
            
            // 树形组件配置
            treeProps: {
                label: 'name',
                children: 'children'
            },
            defaultExpandedKeys: []
        }
    },
    
    computed: {
        // 是否可以处理
        canProcess() {
            if (this.inputMethod === 'path') {
                return this.folderPath.trim() !== ''
            }
            return this.uploadTaskId !== null
        },
        
        // 排除模式文本
        excludePatternsText: {
            get() {
                return this.config.processing.exclude_patterns.join('\n')
            },
            set(val) {
                this.config.processing.exclude_patterns = val.split('\n').filter(p => p.trim())
            }
        }
    },
    
    mounted() {
        this.loadConfig()
        
        // 定时检查上传任务状态
        setInterval(() => {
            if (this.uploadTaskId) {
                this.checkTaskStatus(this.uploadTaskId)
            }
        }, 2000)
    },
    
    methods: {
        // 加载配置
        async loadConfig() {
            try {
                const res = await axios.get('/api/config')
                this.config = res.data
            } catch (err) {
                console.error('加载配置失败', err)
            }
        },
        
        // 保存配置
        async saveConfig() {
            try {
                await axios.put('/api/config', this.config)
                this.$message.success('配置已保存')
                this.showConfig = false
            } catch (err) {
                this.$message.error('保存配置失败')
            }
        },
        
        // 预览文件夹结构
        async previewFolder() {
            if (!this.folderPath.trim()) {
                this.$message.warning('请输入文件夹路径')
                return
            }
            
            try {
                const res = await axios.post('/api/preview', {
                    folder_path: this.folderPath
                })
                this.previewTree = res.data.tree
                this.$message.success('预览成功')
            } catch (err) {
                this.$message.error(err.response?.data?.error || '预览失败')
            }
        },
        
        // 处理文件夹
        async processFolder() {
            this.processing = true
            
            try {
                const res = await axios.post('/api/process', {
                    folder_path: this.folderPath,
                    config: this.config
                })
                
                this.result = res.data.result
                this.$message.success('处理完成')
            } catch (err) {
                this.$message.error(err.response?.data?.error || '处理失败')
            } finally {
                this.processing = false
            }
        },
        
        // 上传前检查
        beforeUpload(file) {
            const isValidType = file.name.endsWith('.zip') || 
                               file.name.endsWith('.tar') || 
                               file.name.endsWith('.tar.gz')
            if (!isValidType) {
                this.$message.error('只支持 .zip, .tar, .tar.gz 格式')
                return false
            }
            
            const isLt500M = file.size / 1024 / 1024 < 500
            if (!isLt500M) {
                this.$message.error('文件大小不能超过 500MB')
                return false
            }
            
            return true
        },
        
        // 上传成功
        handleUploadSuccess(res) {
            if (res.success) {
                this.uploadTaskId = res.task_id
                this.uploadProgress = 0
                this.uploadStatus = null
                this.$message.success('文件上传成功，开始处理...')
            } else {
                this.$message.error(res.error || '上传失败')
            }
        },
        
        // 上传失败
        handleUploadError(err) {
            this.$message.error('上传失败: ' + (err.message || '网络错误'))
        },
        
        // 检查任务状态
        async checkTaskStatus(taskId) {
            try {
                const res = await axios.get(`/api/task/${taskId}`)
                const task = res.data
                
                if (task.progress !== undefined) {
                    this.uploadProgress = task.progress
                }
                this.uploadMessage = task.message || ''
                
                if (task.status === 'completed') {
                    this.uploadStatus = 'success'
                    this.result = task.result
                    this.$message.success('处理完成')
                    this.uploadTaskId = null
                    
                    // 构建预览树
                    if (task.result && task.result.tree) {
                        this.previewTree = task.result.tree
                    }
                } else if (task.status === 'failed') {
                    this.uploadStatus = 'exception'
                    this.$message.error(task.error || '处理失败')
                    this.uploadTaskId = null
                }
            } catch (err) {
                console.error('检查任务状态失败', err)
            }
        },
        
        // 格式化进度显示
        formatProgress(percentage) {
            return `${percentage}%`
        },
        
        // 下载结果
        downloadResult() {
            if (!this.result) return
            
            const dataStr = JSON.stringify(this.result, null, 2)
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
            
            const exportFileDefaultName = `folder2context_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.json`
            
            const linkElement = document.createElement('a')
            linkElement.setAttribute('href', dataUri)
            linkElement.setAttribute('download', exportFileDefaultName)
            linkElement.click()
        },
        
        // 清空预览
        clearPreview() {
            this.previewTree = null
            this.folderPath = ''
        }
    }
})