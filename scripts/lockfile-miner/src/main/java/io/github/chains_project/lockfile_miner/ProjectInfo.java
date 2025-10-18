package io.github.chains_project.lockfile_miner;

import org.kohsuke.github.GHRepository;

import java.util.List;

/**
 * Class to hold project type and lockfile existence.
 */
public record ProjectInfo(GHRepository repository, List<RepositoryFilters.ProjectType> projectType, boolean lockfileExists) {

    @Override
    public String toString() {
        return "ProjectInfo{" +
                "projectType=" + projectType +
                ", lockfileExists=" + lockfileExists +
                '}';
    }
}

