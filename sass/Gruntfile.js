module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    sass: {
      options: {
        outputStyle: 'compressed',
	spawn: false
      },
      dist: {
        files: {
          '../billiards/static/css/m/v3.css': 'billiards/cqkozo.scss',
        }        
      },
    },

    watch: {
      grunt: { files: ['Gruntfile.js'] },

      sass: {
        files: ['billiards/*.scss'],
        tasks: ['sass']
      }
    }
  });

  grunt.loadNpmTasks('grunt-sass');
  grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('build', ['sass']);
  grunt.registerTask('default', ['build','watch']);
}
