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

CREATE TABLE scan_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

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

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id),
    permission_id UUID REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    details JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_members (
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    PRIMARY KEY (project_id, user_id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE,
    inactivated_by UUID REFERENCES users(id)
);

CREATE TABLE user_groups (
    user_id UUID REFERENCES users(id),
    group_id UUID REFERENCES groups(id),
    PRIMARY KEY (user_id, group_id),
    active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    inactive_at TIMESTAMP WITH TIME ZONE
);

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
