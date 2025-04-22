CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    preferences JSONB DEFAULT '{}'::jsonb,
    feature_flags JSONB DEFAULT '{}'::jsonb,
    password_hash TEXT,
    external_id TEXT,
    idp_provider TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_users_active ON users (inactive_at);
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_username ON users (username);

CREATE TABLE scan_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_scan_types_active ON scan_types (inactive_at);
CREATE INDEX idx_scan_types_name ON scan_types (name);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    parent_id UUID REFERENCES projects(id),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dashboard_config JSONB DEFAULT '{}'::jsonb,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_projects_active ON projects (inactive_at);
CREATE INDEX idx_projects_name ON projects (name);
CREATE INDEX idx_projects_parent_id ON projects (parent_id);

CREATE TABLE scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    scan_type TEXT NOT NULL,
    scan_result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    project_id UUID REFERENCES projects(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_scans_active ON scans (inactive_at);
CREATE INDEX idx_scans_project_id ON scans (project_id);
CREATE INDEX idx_scans_user_id ON scans (user_id);
CREATE INDEX idx_scans_scan_type ON scans (scan_type);

CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id UUID REFERENCES scans(id),
    artifact_name TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    project_id UUID REFERENCES projects(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_artifacts_active ON artifacts (inactive_at);
CREATE INDEX idx_artifacts_project_id ON artifacts (project_id);
CREATE INDEX idx_artifacts_scan_id ON artifacts (scan_id);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_roles_active ON roles (inactive_at);
CREATE INDEX idx_roles_name ON roles (name);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_permissions_active ON permissions (inactive_at);
CREATE INDEX idx_permissions_name ON permissions (name);

CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id),
    permission_id UUID REFERENCES permissions(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX idx_role_permissions_active ON role_permissions (inactive_at);
CREATE INDEX idx_role_permissions_role_id ON role_permissions (role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions (permission_id);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX idx_user_roles_active ON user_roles (inactive_at);
CREATE INDEX idx_user_roles_user_id ON user_roles (user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles (role_id);

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_logs_user_id ON activity_logs (user_id);
CREATE INDEX idx_activity_logs_action ON activity_logs (action);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs (timestamp);

CREATE TABLE project_members (
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (project_id, user_id)
);

CREATE INDEX idx_project_members_active ON project_members (inactive_at);
CREATE INDEX idx_project_members_project_id ON project_members (project_id);
CREATE INDEX idx_project_members_user_id ON project_members (user_id);

CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_groups_active ON groups (inactive_at);
CREATE INDEX idx_groups_name ON groups (name);

CREATE TABLE user_groups (
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES groups(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, group_id)
);

CREATE INDEX idx_user_groups_active ON user_groups (inactive_at);
CREATE INDEX idx_user_groups_user_id ON user_groups (user_id);
CREATE INDEX idx_user_groups_group_id ON user_groups (group_id);

-- Project group permissions and membership
CREATE TABLE project_group_members (
    project_id UUID REFERENCES projects(id),
    group_id UUID REFERENCES groups(id),
    role_id UUID REFERENCES roles(id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (project_id, group_id)
);

CREATE INDEX idx_project_group_members_active ON project_group_members (inactive_at);
CREATE INDEX idx_project_group_members_project_id ON project_group_members (project_id);
CREATE INDEX idx_project_group_members_group_id ON project_group_members (group_id);

CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    key_hash TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_api_keys_active ON api_keys (inactive_at);
CREATE INDEX idx_api_keys_user_id ON api_keys (user_id);
CREATE INDEX idx_api_keys_project_id ON api_keys (project_id);

CREATE TABLE secrets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    value_enc BYTEA NOT NULL,
    user_id UUID REFERENCES users(id),
    project_id UUID REFERENCES projects(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE,
    updated_by UUID REFERENCES users(id),
    rotated_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE,
    description TEXT,
    type TEXT, -- e.g. "pipeline", "user", "api", etc.
    metadata JSONB DEFAULT '{}'::jsonb,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE INDEX idx_secrets_active ON secrets (inactive_at);
CREATE INDEX idx_secrets_user_id ON secrets (user_id);
CREATE INDEX idx_secrets_project_id ON secrets (project_id);
CREATE INDEX idx_secrets_name ON secrets (name);
