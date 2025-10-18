package io.github.chains_project.lockfile_miner;

import org.kohsuke.github.GHCommit;
import org.kohsuke.github.GHRepository;
import org.kohsuke.github.GHTreeEntry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.temporal.ChronoUnit;
import java.io.IOException;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.*;
import java.util.stream.Collectors;

/**
 * The RepositoryFilters class contains predicates over GitHub repositories
 * and methods that can be used to filter for repositories having certain properties.
 */
public class RepositoryFilters {
    private static final Logger log = LoggerFactory.getLogger(RepositoryFilters.class);

    private RepositoryFilters() { /* Nothing to see here... */ }

    /**
     * Identifies the type of project (Maven, Gradle, npm, pnpm, pipenv, Poetry, Cargo, Go)
     * and checks for the existence of lockfiles in the main branch of a GitHub repository.
     *
     * @return a ProjectInfo object containing the identified ProjectTypes and
     * a boolean indicating whether at least one corresponding lockfile exists.
     */
    public static ProjectInfo identifyProjectTypeAndLockfile(GHRepository repository, String projectType) {
        try {
            List<GHTreeEntry> treeEntries = repository.getTree(repository.getDefaultBranch()).getTree();
            Set<String> filePaths = treeEntries.stream()
                    .map(GHTreeEntry::getPath)
                    .collect(Collectors.toSet());

            Map<ProjectType, ProjectFilePatterns> projectFilePatterns = Map.of(
                    ProjectType.NPM, new ProjectFilePatterns("package.json", "package-lock.json"),
                    ProjectType.PNPM, new ProjectFilePatterns("package.json", "pnpm-lock.yaml"),
                    ProjectType.CARGO, new ProjectFilePatterns("Cargo.toml", "Cargo.lock"),
                    ProjectType.POETRY, new ProjectFilePatterns("pyproject.toml", "poetry.lock"),
                    ProjectType.PIPENV, new ProjectFilePatterns("Pipfile", "Pipfile.lock"),
                    ProjectType.GRADLE, new ProjectFilePatterns(Arrays.asList("build.gradle", "build.gradle.kts"), "gradle.lockfile"),
                    ProjectType.GO, new ProjectFilePatterns("go.mod", "go.sum")
            );

            List<ProjectType> detectedProjects = new ArrayList<>();
            List<ProjectType> projectsWithLockfile = new ArrayList<>();

            for (Map.Entry<ProjectType, ProjectFilePatterns> entry : projectFilePatterns.entrySet()) {
                ProjectType type = entry.getKey();
                ProjectFilePatterns patterns = entry.getValue();

                if (!projectType.equalsIgnoreCase(type.name())) {
                    continue;
                }

                boolean hasManifest = patterns.getManifests().stream()
                        .anyMatch(filePaths::contains);
                boolean hasLock = patterns.getLockfiles().stream()
                        .anyMatch(filePaths::contains);

                if (hasManifest) {
                    detectedProjects.add(type);
                    if (hasLock) {
                        projectsWithLockfile.add(type);
                    }
                }
            }

            if (detectedProjects.isEmpty() && projectsWithLockfile.isEmpty()) {
                return null;
            }

            boolean hasLockfile = !projectsWithLockfile.isEmpty();
            return new ProjectInfo(repository, detectedProjects, hasLockfile);

        } catch (IOException e) {
            throw new RuntimeException("Failed to check repository structure", e);
        }
    }

    /**
     * Helper class to group manifest and lockfile patterns for each project type.
     */
    static class ProjectFilePatterns {
        private final List<String> manifests;
        private final List<String> lockfiles;

        public ProjectFilePatterns(String manifest, String lockfile) {
            this.manifests = List.of(manifest);
            this.lockfiles = List.of(lockfile);
        }

        public ProjectFilePatterns(List<String> manifests, String lockfile) {
            this.manifests = manifests;
            this.lockfiles = List.of(lockfile);
        }

        public List<String> getManifests() {
            return manifests;
        }

        public List<String> getLockfiles() {
            return lockfiles;
        }
    }

    /**
     * Check if a given repository has sufficient number of commits.
     */
    public static boolean hasSufficientNumberOfCommits(GHRepository repository, int minNumberOfCommits) {
        try {
            return repository.listCommits().toList().size() >= minNumberOfCommits;
        } catch (IOException e) {
            log.error("Search for GitHub repo {} failed : ", repository.getFullName(), e);
            return false;
        }
    }

    /**
     * Check if a given repository has sufficient number of contributors.
     */
    public static boolean hasSufficientNumberOfContributors(GHRepository repository, int minNumberOfContributors) {
        try {
            return repository.listContributors().toList().size() >= minNumberOfContributors;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public static boolean isLastCommitWithinThreeMonths(GHRepository repository) {
        try {
            List<GHCommit> commits = repository.listCommits().toList();
            if (!commits.isEmpty()) {
                LocalDate lastCommitDate = commits.get(0).getCommitDate().toInstant()
                        .atZone(ZoneId.systemDefault()).toLocalDate();
                LocalDate threeMonthsAgo = LocalDate.now().minus(3, ChronoUnit.MONTHS);
                return lastCommitDate.isAfter(threeMonthsAgo);
            }
        } catch (IOException e) {
            log.error("Error retrieving commits for repository: " + repository.getFullName(), e);
        }
        return false;
    }

    /**
     * Enum representing different project types based on the build system.
     */
    public enum ProjectType {
        GRADLE, NPM, YARN, NPMSHRINK, PNPM, npm, PIPENV, CARGO, POETRY, GO
    }
}
