INSERT INTO tickets (ticket_id, title, status, created_by)
VALUES
    ('10000000-0000-4000-8000-000000000001', 'Cannot access analytics dashboard', 'open', 'sample-user'),
    ('10000000-0000-4000-8000-000000000002', 'Request access to finance catalog', 'in_progress', 'sample-user'),
    ('10000000-0000-4000-8000-000000000003', 'Scheduled job reports a timeout', 'resolved', 'sample-user')
ON CONFLICT (ticket_id) DO NOTHING;

INSERT INTO ticket_messages (message_id, ticket_id, message_text, author)
VALUES
    ('20000000-0000-4000-8000-000000000001', '10000000-0000-4000-8000-000000000001', 'The dashboard returns an authorization error.', 'sample-user'),
    ('20000000-0000-4000-8000-000000000002', '10000000-0000-4000-8000-000000000001', 'I confirmed the workspace login is active.', 'sample-user'),
    ('20000000-0000-4000-8000-000000000003', '10000000-0000-4000-8000-000000000002', 'Please add me to the finance reporting group.', 'sample-user'),
    ('20000000-0000-4000-8000-000000000004', '10000000-0000-4000-8000-000000000002', 'The request is being reviewed by the data owner.', 'sample-user'),
    ('20000000-0000-4000-8000-000000000005', '10000000-0000-4000-8000-000000000003', 'The nightly refresh exceeded its usual duration.', 'sample-user'),
    ('20000000-0000-4000-8000-000000000006', '10000000-0000-4000-8000-000000000003', 'The warehouse setting was adjusted and the job completed.', 'sample-user')
ON CONFLICT (message_id) DO NOTHING;
