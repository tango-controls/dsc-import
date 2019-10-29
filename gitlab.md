# Integration of a GitLab repository with the Device Classes Catalogue

To integrate a GitLab device server repository with the catalogue (to allow for automatic catalogue entries creation or updates) it is proposed to do the following:

- Create a dedicated functional account on the Tango Controls webpage. This account will be used for script authorisation. 

- Fork the [dsc-import script](https://github.com/tango-controls/dsc-import) to your GitLab organisation. This is to keep control
  on the code which you are running on your infrastructure. It makes also easy to patch the importing code with specific updates
  and use the right version of the script.
  From time to time it is worth to update this local copy with the recent updates in the GitHub upstream. Also, sending pull
  requests for new features implemented could be a good idea :-).    

- Create a dedicated common repository which will provide a `.dsc-update-base.yml` file with`.dsc-update-base` job. 
  This job will have a base configuration for the catalogue updates. See examples in the [dsc-import script](https://github.com/tango-controls/dsc-import)

- In your device server repository, add a `.cataluge-update.yml` which includes `.dsc-update-base.yml` and extend 
  `dsc-update-base` job with information specific to this device server (use of the GitLab *variables* yml command, see [this](https://docs.gitlab.com/ee/ci/variables/#via-gitlab-ciyml) ).

- Include the `.catalogue-update.yml` in the repository main CI/CD configuration (`.gitlab-ci.yml`).

- To avoid disclosure of your credentials, configure `DSC_LOGIN` and `DSC_PASSWORD` variables 
  [via UI](https://docs.gitlab.com/ee/ci/variables/#via-the-ui).

The proposed include structure is to separate catalogue update configuration from other CI/CD settings.
